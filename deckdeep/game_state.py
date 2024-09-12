from enum import Enum, auto
from typing import Dict, List, Callable, Tuple, Optional, TYPE_CHECKING
from functools import wraps

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
        self.transition_map: Dict[GameState, List[Tuple[str, GameState]]] = {
            GameState.MAIN_MENU: [
                ("Start Game", GameState.NODE_SELECTION),
                ("Load Game", GameState.NODE_SELECTION),
                ("Enter Combat", GameState.COMBAT_START),
                ("Start Game", GameState.COMBAT_START),
            ],
            GameState.NODE_SELECTION: [
                ("Enter Combat", GameState.COMBAT_START),
                ("Enter Event", GameState.EVENT),
                ("Enter Rest Site", GameState.REST_SITE),
                ("Enter Treasure Room", GameState.TREASURE_ROOM),
            ],
            GameState.COMBAT_START: [
                ("Start Player Turn", GameState.COMBAT_PLAYER_TURN),
            ],
            GameState.COMBAT_PLAYER_TURN: [
                ("End Player Turn", GameState.COMBAT_MONSTER_TURN),
                ("View Deck", GameState.DECK_VIEW),
                ("View Relics", GameState.RELIC_VIEW),
                ("Combat Completed", GameState.COMBAT_END),  # Changed from NODE_SELECTION to COMBAT_END
            ],
            GameState.COMBAT_MONSTER_TURN: [
                ("End Combat", GameState.COMBAT_END),  # Changed from COMBAT_END to COMBAT_START
                ("Next Combat Round", GameState.COMBAT_START),
            ],
            GameState.COMBAT_END: [
                ("Next Combat Round", GameState.COMBAT_START),
                ("Victory", GameState.CARD_SELECT),  # Changed from VICTORY_SCREEN to CARD_SELECT
                ("Defeat", GameState.GAME_OVER),
                ("Player Died", GameState.GAME_OVER),
            ],
            GameState.EVENT: [
                ("Event Completed", GameState.NODE_SELECTION),
            ],
            GameState.REST_SITE: [
                ("Rest Completed", GameState.NODE_SELECTION),
            ],
            GameState.TREASURE_ROOM: [
                ("Treasure Collected", GameState.NODE_SELECTION),
            ],
            GameState.VICTORY_SCREEN: [
                ("Continue", GameState.NODE_SELECTION),
                ("Continue to Next Node", GameState.NODE_SELECTION),
            ],
            GameState.GAME_OVER: [
                ("Game Over", GameState.MAIN_MENU),
            ],
            GameState.DECK_VIEW: [
                ("Return to Combat", GameState.COMBAT_PLAYER_TURN),
            ],
            GameState.RELIC_VIEW: [
                ("Return to Combat", GameState.COMBAT_PLAYER_TURN),
            ],
            GameState.CARD_SELECT: [
                ("Card Selected", GameState.NODE_SELECTION),
                ("Skip Card", GameState.NODE_SELECTION),
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

    def transition_to(self, new_state: GameState, transition_reason: str):
        valid_transitions = self.transition_map.get(self.current_state, [])
        for reason, state in valid_transitions:
            if state == new_state and reason == transition_reason:
                self.game.logger.info(f"Transitioning from {self.current_state} to {new_state}: {transition_reason}", category="STATE")
                self.current_state = new_state
                return
        raise ValueError(f"Invalid transition from {self.current_state} to {new_state} with reason: {transition_reason}")

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

    def get_valid_transitions(self) -> List[Tuple[str, GameState]]:
        return self.transition_map.get(self.current_state, [])