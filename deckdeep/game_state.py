from enum import Enum, auto
from typing import Dict, List, Callable, Tuple, Optional, TYPE_CHECKING
from functools import wraps
from deckdeep.node import NodeType
if TYPE_CHECKING:
    from game import Game

class GameState(Enum):
    MAIN_MENU = auto()
    NODE_SELECTION = auto()
    COMBAT_START = auto()
    COMBAT_PLAYER_TURN = auto()
    COMBAT_MONSTER_TURN = auto()
    COMBAT_END = auto()
    EVENT = auto()
    REST_SITE = auto()
    TREASURE_ROOM = auto()
    VICTORY_SCREEN = auto()
    GAME_OVER = auto()
    DECK_VIEW = auto()
    RELIC_VIEW = auto()
    CARD_SELECT = auto()

class TransitionReason(Enum):
    START_GAME = "Start Game"
    LOAD_GAME = "Load Game"
    ENTER_COMBAT = "Enter Combat"
    ENTER_EVENT = "Enter Event"
    ENTER_REST_SITE = "Enter Rest Site"
    ENTER_TREASURE_ROOM = "Enter Treasure Room"
    START_PLAYER_TURN = "Start Player Turn"
    END_PLAYER_TURN = "End Player Turn"
    VIEW_DECK = "View Deck"
    VIEW_RELICS = "View Relics"
    COMBAT_COMPLETED = "Combat Completed"
    END_COMBAT = "End Combat"
    NEXT_COMBAT_ROUND = "Next Combat Round"
    VICTORY = "Victory"
    DEFEAT = "Defeat"
    PLAYER_DIED = "Player Died"
    EVENT_COMPLETED = "Event Completed"
    REST_COMPLETED = "Rest Completed"
    TREASURE_COLLECTED = "Treasure Collected"
    CONTINUE = "Continue"
    GAME_OVER = "Game Over"
    RETURN_TO_COMBAT = "Return to Combat"
    CARD_SELECTED = "Card Selected"
    SKIP_CARD = "Skip Card"

def state_handler(state: GameState):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        wrapper.handled_state = state
        return wrapper
    return decorator

def key_handler(state: GameState):
    def decorator(func):
        @wraps(func)
        def wrapper(self, key_name: str, *args, **kwargs):
            return func(self, key_name, *args, **kwargs)
        wrapper.key_handled_state = state
        return wrapper
    return decorator

def renderer(state: GameState):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        wrapper.rendered_state = state
        return wrapper
    return decorator

class GameStateMachine:
    def __init__(self, game: "Game"):
        self.game = game
        self.current_state = GameState.MAIN_MENU
        self.state_handlers: Dict[GameState, Callable] = {}
        self.key_handlers: Dict[GameState, Callable] = {}
        self.renderers: Dict[GameState, Callable] = {}
        self.transition_map: Dict[GameState, List[Tuple[TransitionReason, GameState]]] = {
            GameState.MAIN_MENU: [
                (TransitionReason.START_GAME, GameState.NODE_SELECTION),
                (TransitionReason.LOAD_GAME, GameState.NODE_SELECTION),
                (TransitionReason.ENTER_COMBAT, GameState.COMBAT_START),
            ],
            GameState.NODE_SELECTION: [
                (TransitionReason.ENTER_COMBAT, GameState.COMBAT_START),
                (TransitionReason.ENTER_EVENT, GameState.EVENT),
                (TransitionReason.ENTER_REST_SITE, GameState.REST_SITE),
                (TransitionReason.ENTER_TREASURE_ROOM, GameState.TREASURE_ROOM),
            ],
            GameState.COMBAT_START: [
                (TransitionReason.START_PLAYER_TURN, GameState.COMBAT_PLAYER_TURN),
            ],
            GameState.COMBAT_PLAYER_TURN: [
                (TransitionReason.END_PLAYER_TURN, GameState.COMBAT_MONSTER_TURN),
                (TransitionReason.VIEW_DECK, GameState.DECK_VIEW),
                (TransitionReason.VIEW_RELICS, GameState.RELIC_VIEW),
                (TransitionReason.COMBAT_COMPLETED, GameState.COMBAT_END),
            ],
            GameState.COMBAT_MONSTER_TURN: [
                (TransitionReason.COMBAT_COMPLETED, GameState.COMBAT_END),
                (TransitionReason.NEXT_COMBAT_ROUND, GameState.COMBAT_START),
            ],
            GameState.COMBAT_END: [
                (TransitionReason.NEXT_COMBAT_ROUND, GameState.COMBAT_START),
                (TransitionReason.VICTORY, GameState.CARD_SELECT),
                (TransitionReason.DEFEAT, GameState.GAME_OVER),
                (TransitionReason.PLAYER_DIED, GameState.GAME_OVER),
            ],
            GameState.EVENT: [
                (TransitionReason.EVENT_COMPLETED, GameState.NODE_SELECTION),
            ],
            GameState.REST_SITE: [
                (TransitionReason.REST_COMPLETED, GameState.NODE_SELECTION),
            ],
            GameState.TREASURE_ROOM: [
                (TransitionReason.TREASURE_COLLECTED, GameState.NODE_SELECTION),
            ],
            GameState.VICTORY_SCREEN: [
                (TransitionReason.CONTINUE, GameState.NODE_SELECTION),
            ],
            GameState.GAME_OVER: [
                (TransitionReason.GAME_OVER, GameState.MAIN_MENU),
            ],
            GameState.DECK_VIEW: [
                (TransitionReason.RETURN_TO_COMBAT, GameState.COMBAT_PLAYER_TURN),
            ],
            GameState.RELIC_VIEW: [
                (TransitionReason.RETURN_TO_COMBAT, GameState.COMBAT_PLAYER_TURN),
            ],
            GameState.CARD_SELECT: [
                (TransitionReason.CARD_SELECTED, GameState.NODE_SELECTION),
                (TransitionReason.SKIP_CARD, GameState.NODE_SELECTION),
            ],
        }
        self._register_handlers()

    def _register_handlers(self):
        for attr_name in dir(self.game):
            attr = getattr(self.game, attr_name)
            if hasattr(attr, 'handled_state'):
                self.state_handlers[attr.handled_state] = attr
            if hasattr(attr, 'key_handled_state'):
                self.key_handlers[attr.key_handled_state] = attr
            if hasattr(attr, 'rendered_state'):
                self.renderers[attr.rendered_state] = attr

    def transition_to(self, new_state: GameState, transition_reason: TransitionReason):
        valid_transitions = self.transition_map.get(self.current_state, [])
        for reason, state in valid_transitions:
            if state == new_state and reason == transition_reason:
                self.game.logger.info(f"Transitioning from {self.current_state} to {new_state}: {transition_reason.value}", category="STATE")
                self.current_state = new_state
                return
        raise ValueError(f"Invalid transition from {self.current_state} to {new_state} with reason: {transition_reason.value}")

    def update(self):
        handler = self.state_handlers.get(self.current_state)
        if handler:
            handler()

    def handle_key_press(self, key_name: str):
        handler = self.key_handlers.get(self.current_state)
        if handler:
            handler(key_name)

    def render(self):
        renderer = self.renderers.get(self.current_state)
        if renderer:
            renderer()

    def get_valid_transitions(self) -> List[Tuple[TransitionReason, GameState]]:
        return self.transition_map.get(self.current_state, [])

    def get_transition_reason_for_node_type(self, node_type) -> TransitionReason:
        if node_type in [NodeType.MONSTER, NodeType.ELITE, NodeType.BOSS]:
            return TransitionReason.ENTER_COMBAT
        elif node_type == NodeType.EVENT:
            return TransitionReason.ENTER_EVENT
        elif node_type == NodeType.REST:
            return TransitionReason.ENTER_REST_SITE
        elif node_type == NodeType.TREASURE:
            return TransitionReason.ENTER_TREASURE_ROOM
        else:
            raise ValueError(f"Invalid node type: {node_type}")