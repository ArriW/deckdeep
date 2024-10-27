import pygame
import sys
from deckdeep.game_state import GameState, GameStateMachine, TransitionReason, state_handler, key_handler, renderer, on_enter, on_exit
from deckdeep.assets import GameAssets
from deckdeep.player import Player
from deckdeep.monster_group import MonsterGroup
from deckdeep.map_generator import MapGenerator
from deckdeep.logger import GameLogger
from deckdeep.music_manager import BackgroundMusicManager
from deckdeep.render import (
    render_start_screen, render_node_selection, render_combat_state,
    render_text_event, render_victory_state, render_deck_view, render_relic_view
)
from deckdeep.node import NodeType
from deckdeep.card import Card
from deckdeep.events import get_random_event
from deckdeep.custom_types import TriggerWhen
import random
from deckdeep.config import CARD_WIDTH, CARD_SPACING, CARD_HEIGHT

import os
import json

from typing import List, Optional


class Game:
    def __init__(self, screen, logger: GameLogger):
        self.screen: pygame.Surface = screen
        self.logger: GameLogger = logger
        self.assets: GameAssets = GameAssets()
        self.player: Player = None
        self.monster_group: MonsterGroup = None
        self.node_map: List[List[Node]] = None
        self.current_node: Node = None
        self.stage: int = 1
        self.score = 0
        self.running = True
        self.clock = pygame.time.Clock()
        self.map_generator = MapGenerator()
        self.state_machine = GameStateMachine(self)
        self.current_event = None
        self.text_event_selection = 0
        self.player_turn = True
        self.monster_intentions = []
        self.played_cards = []
        self.current_page = 0
        self.cards_per_page = 15
        self.selected_card = -1
        self.new_cards = []

    def run(self):
        # Don't transition here, just set the initial state
        self.state_machine.current_state = GameState.MAIN_MENU
        
        with BackgroundMusicManager(self.assets.music_path) as music_manager:
            while self.running:
                self.handle_events(music_manager)
                self.state_machine.update()
                self.state_machine.render()
                pygame.display.flip()
                self.clock.tick(60)

        self.cleanup()

    def handle_events(self, music_manager: BackgroundMusicManager):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.state_machine.handle_key_press(pygame.key.name(event.key).upper())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            music_manager.handle_event(event)

    def handle_mouse_click(self, pos):
        if self.state_machine.current_state == GameState.COMBAT_PLAYER_TURN:
            self.select_card(pos[0], pos[1])
            self.play_card()

    @state_handler(GameState.MAIN_MENU)
    def handle_main_menu(self):
        if not self.player:
            if self.check_save_file():
                if self.load_game():
                    self.state_machine.transition_to(GameState.NODE_SELECTION, TransitionReason.LOAD_GAME)
                else:
                    self.new_game()
                    self.state_machine.transition_to(GameState.COMBAT_START, TransitionReason.START_GAME)
            else:
                self.new_game()
                self.state_machine.transition_to(GameState.COMBAT_START, TransitionReason.ENTER_COMBAT)
        else:
            # If player exists, we're returning from game over, so reset the game
            self.new_game()
            self.state_machine.transition_to(GameState.COMBAT_START, TransitionReason.START_GAME)

    @key_handler(GameState.MAIN_MENU)
    def handle_main_menu_key_press(self, key_name: str):
        if key_name == "RETURN":
            self.state_machine.transition_to(GameState.NODE_SELECTION, TransitionReason.START_GAME)

    @renderer(GameState.MAIN_MENU)
    def render_main_menu(self):
        render_start_screen(self.screen, self.assets)

    @state_handler(GameState.NODE_SELECTION)
    def handle_node_selection(self):
        available_nodes = [node for node in self.current_node.children if node is not None]
        if not available_nodes:
            self.next_stage()

    @key_handler(GameState.NODE_SELECTION)
    def handle_node_selection_key_press(self, key_name: str):
        available_nodes = [node for node in self.current_node.children if node is not None]
        if key_name in ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]:
            index = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"].index(key_name)
            if index < len(available_nodes):
                self.current_node = available_nodes[index]
                self.initialize_node()
                transition_reason = self.state_machine.get_transition_reason_for_node_type(self.current_node.node_type)
                new_state = self.get_state_for_node_type(self.current_node.node_type)
                self.state_machine.transition_to(new_state, transition_reason)

    def get_state_for_node_type(self, node_type):
        if node_type in [NodeType.MONSTER, NodeType.ELITE, NodeType.BOSS]:
            return GameState.COMBAT_START
        elif node_type == NodeType.EVENT:
            return GameState.EVENT
        elif node_type == NodeType.REST:
            return GameState.REST_SITE
        elif node_type == NodeType.TREASURE:
            return GameState.TREASURE_ROOM
        else:
            return GameState.NODE_SELECTION

    @renderer(GameState.NODE_SELECTION)
    def render_node_selection(self):
        available_nodes = [node for node in self.current_node.children if node is not None]
        render_node_selection(
            self.screen,
            self.node_map,
            self.current_node,
            available_nodes,
            0,  # selected_index is not used in this implementation
            self.assets,
            self.player,
        )

    @on_enter(GameState.COMBAT_START)
    def on_enter_combat_start(self):
        self.player.reset_energy()
        self.player.draw_hand()
        self.player.apply_status_effects(TriggerWhen.COMBAT_START)
        self.monster_group.apply_status_effects(TriggerWhen.COMBAT_START)
        self.logger.info("Entered combat start state", category="COMBAT")

    @state_handler(GameState.COMBAT_START)
    def handle_combat_start(self):
        # is this needed?
        if self.check_combat_end():
            return
        self.state_machine.transition_to(GameState.COMBAT_PLAYER_TURN, TransitionReason.START_PLAYER_TURN)

    @on_enter(GameState.COMBAT_PLAYER_TURN)
    def on_enter_combat_player_turn(self):
        self.player.apply_status_effects(TriggerWhen.TURN_START)

    @state_handler(GameState.COMBAT_PLAYER_TURN)
    def handle_combat_player_turn(self):
        if self.check_combat_end():
            return

    @on_exit(GameState.COMBAT_PLAYER_TURN)
    def on_exit_combat_player_turn(self):
        self.player.end_turn()

    @key_handler(GameState.COMBAT_PLAYER_TURN)
    def handle_combat_player_turn_key_press(self, key_name: str):
        if key_name == "SPACE":
            if self.check_combat_end():
                return
            self.state_machine.transition_to(GameState.COMBAT_MONSTER_TURN, TransitionReason.END_PLAYER_TURN)
        elif key_name in ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]:
            index = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"].index(key_name)
            if index < len(self.player.hand):
                self.selected_card = index
                self.play_card()
        elif key_name == "H":
            self.monster_group.select_previous()
        elif key_name == "L":
            self.monster_group.select_next()
        elif key_name == "1":
            self.state_machine.transition_to(GameState.DECK_VIEW, TransitionReason.VIEW_DECK)
        elif key_name == "2":
            self.state_machine.transition_to(GameState.RELIC_VIEW, TransitionReason.VIEW_RELICS)

    @renderer(GameState.COMBAT_PLAYER_TURN)
    def render_combat(self):
        render_combat_state(
            self.screen,
            self.player,
            self.monster_group,
            self.player.hand,
            self.player_turn,
            self.monster_intentions,
            f"Level: {self.current_node.y}",
            self.assets,
            self.played_cards,
        )

    @on_enter(GameState.COMBAT_MONSTER_TURN)
    def on_enter_combat_monster_turn(self):
        self.monster_group.apply_status_effects(TriggerWhen.TURN_START)

    @state_handler(GameState.COMBAT_MONSTER_TURN)
    def handle_combat_monster_turn(self):
        self.monster_group.execute_actions(self.player)
        if self.check_combat_end():
            return
        
        self.state_machine.transition_to(GameState.COMBAT_PLAYER_TURN, TransitionReason.NEXT_COMBAT_ROUND)

    @on_exit(GameState.COMBAT_MONSTER_TURN)
    def on_exit_combat_monster_turn(self):
        # self.player.apply_status_effects(TriggerWhen.TURN_END) # HACK 
        self.monster_group.apply_status_effects(TriggerWhen.TURN_END)
        self.monster_group.remove_dead_monsters()



 

    @state_handler(GameState.EVENT)
    def handle_event(self):
        if self.current_event is None:
            self.initialize_event()

    @key_handler(GameState.EVENT)
    def handle_event_key_press(self, key_name: str):
        if key_name in ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]:
            index = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"].index(key_name)
            if index < len(self.current_event.options):
                self.text_event_selection = index
                self.handle_event_selection()
                self.state_machine.transition_to(GameState.NODE_SELECTION, TransitionReason.EVENT_COMPLETED)

    @renderer(GameState.EVENT)
    def render_event(self):
        if self.current_event:
            render_text_event(
                self.screen,
                self.current_event.name,
                self.current_event.description,
                [option[0] for option in self.current_event.options],
                self.assets,
                self.player,
            )

    @state_handler(GameState.REST_SITE)
    def handle_rest_site(self):
        # Implement rest site logic
        self.state_machine.transition_to(GameState.NODE_SELECTION, TransitionReason.REST_COMPLETED)

    @key_handler(GameState.REST_SITE)
    def handle_rest_site_key_press(self, key_name: str):
        # Implement rest site key handling
        pass

    @renderer(GameState.REST_SITE)
    def render_rest_site(self):
        # Implement rest site rendering
        pass

    @state_handler(GameState.TREASURE_ROOM)
    def handle_treasure_room(self):
        # Implement treasure room logic
        self.state_machine.transition_to(GameState.NODE_SELECTION, TransitionReason.TREASURE_COLLECTED)

    @key_handler(GameState.TREASURE_ROOM)
    def handle_treasure_room_key_press(self, key_name: str):
        # Implement treasure room key handling
        pass

    @renderer(GameState.TREASURE_ROOM)
    def render_treasure_room(self):
        # Implement treasure room rendering
        pass

    @state_handler(GameState.VICTORY_SCREEN)
    def handle_victory_screen(self):
        # The actual victory screen handling is done in handle_victory_screen_key_press
        pass

    @key_handler(GameState.VICTORY_SCREEN)
    def handle_victory_screen_key_press(self, key_name: str):
        if key_name in ["Q", "W", "E", "R"]:
            index = ["Q", "W", "E", "R"].index(key_name)
            new_cards = Card.generate_card_pool(3)
            if index < 3:
                self.player.add_card_to_deck(new_cards[index])
            else:
                self.player.increase_max_health(self.player.health_gain_on_skip)
            self.state_machine.transition_to(GameState.NODE_SELECTION, TransitionReason.CONTINUE)

    @renderer(GameState.VICTORY_SCREEN)
    def render_victory_screen(self):
        new_cards = Card.generate_card_pool(3)
        render_victory_state(
            self.screen, new_cards, -1, self.score, self.player, self.assets
        )

    @state_handler(GameState.GAME_OVER)
    def handle_game_over(self):
        self.game_over_screen()
        self.reset_game_state()
        self.state_machine.transition_to(GameState.MAIN_MENU, TransitionReason.GAME_OVER)

    @key_handler(GameState.GAME_OVER)
    def handle_game_over_key_press(self, key_name: str):
        if key_name == "RETURN":
            self.state_machine.transition_to(GameState.MAIN_MENU, TransitionReason.GAME_OVER)

    @renderer(GameState.GAME_OVER)
    def render_game_over(self):
        game_over_image = pygame.transform.scale(
            self.assets.game_over_image, (self.screen.get_width(), self.screen.get_height())
        )
        self.screen.blit(game_over_image, (0, 0))

    @state_handler(GameState.DECK_VIEW)
    def handle_deck_view(self):
        # The actual deck view handling is done in handle_deck_view_key_press
        pass

    @key_handler(GameState.DECK_VIEW)
    def handle_deck_view_key_press(self, key_name: str):
        if key_name == "H":
            self.current_page = max(0, self.current_page - 1)
        elif key_name == "L":
            max_page = (len(self.player.get_sorted_full_deck()) - 1) // self.cards_per_page
            self.current_page = min(max_page, self.current_page + 1)
        elif key_name == "ESCAPE":
            self.state_machine.transition_to(GameState.COMBAT_PLAYER_TURN, TransitionReason.RETURN_TO_COMBAT)

    @renderer(GameState.DECK_VIEW)
    def render_deck_view(self):
        total_pages = (len(self.player.get_sorted_full_deck()) - 1) // self.cards_per_page + 1
        render_deck_view(
            self.screen,
            self.player.get_sorted_full_deck(),
            self.current_page,
            total_pages,
            self.assets,
            self.player,
        )

    @state_handler(GameState.RELIC_VIEW)
    def handle_relic_view(self):
        # The actual relic view handling is done in handle_relic_view_key_press
        pass

    @key_handler(GameState.RELIC_VIEW)
    def handle_relic_view_key_press(self, key_name: str):
        if key_name in ["ESCAPE", "2"]:
            self.state_machine.transition_to
    @renderer(GameState.RELIC_VIEW)
    def render_relic_view(self):
        render_relic_view(self.screen, self.player.relics, self.assets)

    @state_handler(GameState.COMBAT_END)
    def handle_combat_end(self):
        self.player.apply_status_effects(TriggerWhen.COMBAT_END)
        self.monster_group.apply_status_effects(TriggerWhen.COMBAT_END)
        
        if not self.monster_group.has_alive_monsters():
            self.logger.info("Combat victory!", category="COMBAT")
            if self.current_node.node_type == NodeType.BOSS:
                self.state_machine.transition_to(GameState.VICTORY_SCREEN, TransitionReason.VICTORY)
            else:
                self.state_machine.transition_to(GameState.CARD_SELECT, TransitionReason.VICTORY)
        elif self.player.health.value <= 0:
            self.state_machine.transition_to(GameState.GAME_OVER, TransitionReason.PLAYER_DIED)
        else:
            self.state_machine.transition_to(GameState.COMBAT_START, TransitionReason.NEXT_COMBAT_ROUND)

    @state_handler(GameState.CARD_SELECT)
    def handle_card_select(self):
        if not self.new_cards:  # Only generate new cards if the list is empty
            self.new_cards = Card.generate_card_pool(3)

    @key_handler(GameState.CARD_SELECT)
    def handle_card_select_key_press(self, key_name: str):
        if key_name in ["Q", "W", "E", "R"]:
            index = ["Q", "W", "E", "R"].index(key_name)
            if index < 3:
                self.player.add_card_to_deck(self.new_cards[index])
                self.state_machine.transition_to(GameState.NODE_SELECTION, TransitionReason.CARD_SELECTED)
            else:
                self.player.increase_max_health(self.player.health_gain_on_skip)
                self.state_machine.transition_to(GameState.NODE_SELECTION, TransitionReason.SKIP_CARD)
            self.new_cards = []  # Clear the new cards after selection

    @renderer(GameState.CARD_SELECT)
    def render_card_select(self):
        render_victory_state(
            self.screen, self.new_cards, -1, self.score, self.player, self.assets
        )

    def new_game(self):
        self.player = Player.create("Hero", 100, "@")
        self.stage = 1
        self.score = 0
        self.player.reset_hand()
        self.generate_node_map()
        self.current_node = self.map_generator.get_start_node()
        self.logger.info("New game started", category="SYSTEM")
        self.initialize_combat()  # Initialize combat here, but don't transition

    def generate_node_map(self):
        self.node_map = self.map_generator.generate_map()
        self.current_node = self.node_map[0][self.map_generator.width // 2]
        self.logger.info(
            f"Node map generated with {sum(node is not None for row in self.node_map for node in row)} nodes"
        )
        self.map_generator.print_map()

    def initialize_node(self):
        self.logger.debug(f"Initializing node of type: {self.current_node.node_type}")
        if self.current_node.node_type in [NodeType.MONSTER, NodeType.ELITE, NodeType.BOSS]:
            self.initialize_combat()
        elif self.current_node.node_type == NodeType.EVENT:
            self.initialize_event()
        elif self.current_node.node_type == NodeType.REST:
            self.initialize_rest_site()
        elif self.current_node.node_type == NodeType.TREASURE:
            self.initialize_treasure_room()

    def initialize_rest_site(self):
        # Initialize rest site logic
        pass

    def initialize_treasure_room(self):
        # Initialize treasure room logic
        pass


    def initialize_combat(self):
        if "monsters" not in self.current_node.content or not self.current_node.content["monsters"]:
            monster_group, _, _ = MonsterGroup.generate(self.current_node.y)
            self.current_node.content["monsters"] = monster_group

        self.monster_group = self.current_node.content["monsters"]
        if not self.monster_group:
            self.logger.error("Monster group is empty in initialize_combat")
            return

        self.player_turn = True
        self.player.reset_hand()
        self.monster_intentions = self.monster_group.decide_action(self.player)
        self.apply_relic_effects(TriggerWhen.COMBAT_START)

    def initialize_event(self):
        if "event" not in self.current_node.content:
            self.current_node.content["event"] = get_random_event()
        self.current_event = self.current_node.content["event"]
        self.text_event_selection = 0

    def handle_event_selection(self):
        if not self.current_event:
            self.logger.error("Current event is None", category="SYSTEM")
            return

        option_text, option_method = self.current_event.options[self.text_event_selection]
        result = self.current_event.execute_option(option_method, self.player, self.assets)

        for relic in self.player.relics:
            self.logger.debug(f"{relic.name}:{str(relic)}", category="PLAYER")
            if relic.trigger_when == TriggerWhen.PERMANENT:
                msg = relic.apply_effect(self.player, self)
                self.logger.debug(msg, category="PLAYER")
        self.logger.info(f"Event option selected: {option_text}", category="EVENT")
        self.logger.info(f"Event result: {result}", category="EVENT")
        
        self.player.increase_max_energy(1, self.current_node.y)
        self.select_next_node()

    def check_combat_end(self) -> bool:
        if not self.monster_group.has_alive_monsters() or self.player.health.value <= 0:
            self.state_machine.transition_to(GameState.COMBAT_END, TransitionReason.COMBAT_COMPLETED)
            return True
        return False

    def select_card(self, mouse_x: int, mouse_y: int):
        card_start_x = (
            self.screen.get_width()
            - (len(self.player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)
        ) // 2
        for i in range(len(self.player.hand)):
            card_rect = pygame.Rect(
                card_start_x + i * (CARD_WIDTH + CARD_SPACING),
                self.screen.get_height() - CARD_HEIGHT - 20,
                CARD_WIDTH,
                CARD_HEIGHT,
            )
            if card_rect.collidepoint(mouse_x, mouse_y):
                self.selected_card = i
                self.logger.debug(f"Card {i} selected", category="PLAYER")
                break

    def play_card(self):
        if self.selected_card >= 0 and self.selected_card < len(self.player.hand):
            card = self.player.hand[self.selected_card]
            target_monster = self.monster_group.get_selected_monster()

            if target_monster is None or target_monster.is_dying:
                self.logger.debug("No valid monsters to target", category="COMBAT")
                return

            if self.player.energy >= card.energy_cost:
                self.player.apply_status_effects(TriggerWhen.BEFORE_ATTACK)
                self.score += self.player.play_card(card, self.monster_group)
                self.player.apply_status_effects(TriggerWhen.AFTER_ATTACK)
                self.logger.info(
                    f"Player played card: {card.name} on {target_monster.name}",
                    category="COMBAT",
                )
                self.selected_card = -1
            else:
                self.logger.debug("Not enough energy to play the card", category="COMBAT")

    def apply_relic_effects(self, trigger: TriggerWhen):
        for relic in self.player.relics:
            if relic.trigger_when == trigger:
                msg = relic.apply_effect(self.player, self)
                self.logger.debug(msg, category="PLAYER")

    def select_next_node(self):
        available_nodes = [node for node in self.current_node.children if node is not None]
        if available_nodes:
            self.current_node = random.choice(available_nodes)
            self.initialize_node()
        else:
            self.next_stage()

    def next_stage(self):
        self.stage += 1
        self.generate_node_map()
        self.current_node = self.map_generator.get_start_node()
        self.initialize_node()

    def reset_game_state(self):
        self.player = None
        self.monster_group = None
        self.node_map = None
        self.current_node = None
        self.stage = 1
        self.score = 0

    def game_over_screen(self):
        game_over_image = pygame.transform.scale(
            self.assets.game_over_image, (self.screen.get_width(), self.screen.get_height())
        )
        self.screen.blit(game_over_image, (0, 0))
        pygame.display.flip()
        pygame.time.wait(2000)  # Wait for 2 seconds

    def check_save_file(self):
        return os.path.exists("save_game.json")

    def load_game(self):
        try:
            with open("save_game.json", "r") as f:
                save_data = json.load(f)
            self.player = Player.from_dict(save_data["player"])
            self.stage = save_data["stage"]
            self.score = save_data["score"]
            self.current_node = Node.from_dict(save_data["current_node"])
            self.node_map = [[Node.from_dict(node) if node else None for node in row] for row in save_data["node_map"]]
            self.logger.info("Game loaded successfully", category="SYSTEM")
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            self.logger.error("Failed to load game", category="SYSTEM")
            return False


    def save_game(self):
        save_data = {
            "player": self.player.to_dict(),
            "stage": self.stage,
            "score": self.score,
            "current_node": self.current_node.to_dict(),
            "node_map": [[node.to_dict() if node else None for node in row] for row in self.node_map]
        }
        with open("save_game.json", "w") as f:
            json.dump(save_data, f)
        self.logger.info("Game saved successfully", category="SYSTEM")


    def cleanup(self):
        self.save_game()
        pygame.quit()
        sys.exit()
            
