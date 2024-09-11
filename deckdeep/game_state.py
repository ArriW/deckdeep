from enum import Enum, auto

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game

class GameState(Enum):
    MAIN_MENU = auto()
    NODE_SELECTION = auto()
    COMBAT = auto()
    EVENT = auto()
    REST_SITE = auto()
    TREASURE_ROOM = auto()
    VICTORY_SCREEN = auto()
    GAME_OVER = auto()
    DECK_VIEW = auto()
    RELIC_VIEW = auto()

class GameStateMachine:
    def __init__(self, game: "Game"):
        self.game = game
        self.current_state = GameState.MAIN_MENU

    def transition_to(self, new_state: GameState):
        self.game.logger.info(f"Transitioning from {self.current_state} to {new_state}", category="STATE")
        self.current_state = new_state

    def update(self):
        if self.current_state == GameState.MAIN_MENU:
            self.game.handle_main_menu()
        elif self.current_state == GameState.NODE_SELECTION:
            self.game.handle_node_selection()
        elif self.current_state == GameState.COMBAT:
            self.game.handle_combat()
        elif self.current_state == GameState.EVENT:
            self.game.handle_event()
        elif self.current_state == GameState.REST_SITE:
            self.game.handle_rest_site()
        elif self.current_state == GameState.TREASURE_ROOM:
            self.game.handle_treasure_room()
        elif self.current_state == GameState.VICTORY_SCREEN:
            self.game.handle_victory_screen()
        elif self.current_state == GameState.GAME_OVER:
            self.game.handle_game_over()
        elif self.current_state == GameState.DECK_VIEW:
            self.game.handle_deck_view()
        elif self.current_state == GameState.RELIC_VIEW:
            self.game.handle_relic_view()