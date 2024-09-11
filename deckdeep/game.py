import json
import os
import random
import sys
import time
from typing import List, Optional, Tuple

import pygame
from pygame.surface import Surface

from deckdeep.assets import GameAssets
from deckdeep.card import Card
from deckdeep.config import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    CARD_HEIGHT,
    CARD_SPACING,
    CARD_WIDTH,
    END_TURN_BUTTON_X,
    END_TURN_BUTTON_Y,
    KEYBINDS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    VIEW_DECK_BUTTON_X,
    VIEW_DECK_BUTTON_Y,
    scale,
)
from deckdeep.events import (
    AncientLibrary,
    CursedWell,
    DarkMerchant,
    Defender,
    ForgottenShrine,
    Medic,
    Priest,
    RestSite,
    Scribe,
    Thrifter,
    VoodooDoctor,
    get_random_event,
)
from deckdeep.json_encoder import CustomJSONEncoder
from deckdeep.logger import GameLogger
from deckdeep.monster_group import MonsterGroup
from deckdeep.music_manager import BackgroundMusicManager
from deckdeep.player import Player
from deckdeep.relic import Relic, TriggerWhen
from deckdeep.render import (
    render_combat_state,
    render_deck_view,
    render_menu,
    render_node_selection,
    render_relic_selection,
    render_relic_view,
    render_start_screen,
    render_text_event,
    render_victory_state,
    render_keybinds,
)
from deckdeep.status_effect import TriggerType
from deckdeep.map_generator import MapGenerator
from deckdeep.node import Node, NodeType
from deckdeep.game_state import GameStateMachine, GameState

class VictorySequence:
    def __init__(self, screen: Surface, assets: GameAssets):
        self.screen = screen
        self.assets = assets
        self.duration = 2000  # Duration in milliseconds
        self.start_time = 0
        self.particles: List[
            Tuple[int, int, int, Tuple[int, int, int], float, float]
        ] = []

    def start(self):
        self.start_time = pygame.time.get_ticks()
        self.generate_particles()

    def generate_particles(self):
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(5, 15)
            color = random.choice(
                [
                    (255, 215, 0),  # Gold
                    (255, 255, 255),  # White
                    (255, 165, 0),  # Orange
                ]
            )
            speed_x = random.uniform(-1, 1)
            speed_y = random.uniform(-1, 1)
            self.particles.append((x, y, size, color, speed_x, speed_y))

    def update(self):
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration

        if progress >= 1:
            return False

        for i, (x, y, size, color, speed_x, speed_y) in enumerate(self.particles):
            new_x = x + speed_x * 2
            new_y = y + speed_y * 2
            new_size = int(size * (1 - progress))
            self.particles[i] = (
                int(new_x),
                int(new_y),
                new_size,
                color,
                speed_x,
                speed_y,
            )

        return True

    def render(self):
        victory_text = pygame.font.Font(None, scale(100)).render(
            "Victory!", True, (255, 255, 255)
        )
        text_rect = victory_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )

        self.screen.blit(victory_text, text_rect)

        for x, y, size, color, _, _ in self.particles:
            pygame.draw.circle(self.screen, color, (int(x), int(y)), size)

class Game:
    def __init__(self, screen: pygame.Surface, logger: GameLogger):
        self.screen = screen
        self.logger = logger
        self.assets = GameAssets()
        self.player : Player = None
        self.monster_group : MonsterGroup = None
        self.node_map : List[List[Node]] = None
        self.current_node : Node = None
        self.stage = 1
        self.score = 0
        self.selected_card = -1
        self.player_turn = True
        self.running = True
        self.clock = pygame.time.Clock()
        self.menu_options = [
            "Resume",
            "End Turn",
            "View Deck",
            "View Relics",
            "View Keybinds",
            "Save Game",
            "Load Game",
            "Quit",
        ]
        self.menu_selected = 0
        self.text_event_selection = 0
        self.deck_scroll = 0
        self.current_event = None
        self.current_page = 0
        self.cards_per_page = 15
        self.monster_intentions: List[str] = []
        self.played_cards: List[Card] = []
        self.map_generator = MapGenerator()
        self.width = 7
        self.state_machine = GameStateMachine(self)

    def run(self):
        self.state_machine.transition_to(GameState.MAIN_MENU)
        
        with BackgroundMusicManager(self.assets.music_path) as music_manager:
            while self.state_machine.current_state != GameState.GAME_OVER:
                self.handle_events(music_manager)
                self.state_machine.update()
                self.render()
                self.clock.tick(60)

        self.cleanup()

    def cleanup(self):
        pygame.quit()
        sys.exit()

    def handle_events(self, music_manager: BackgroundMusicManager):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state_machine.transition_to(GameState.GAME_OVER)
            elif event.type == pygame.KEYDOWN:
                self.handle_key_press(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            music_manager.handle_event(event)

    def handle_key_press(self, key):
        key_name = pygame.key.name(key).upper()
        current_state = self.state_machine.current_state

        if current_state == GameState.MAIN_MENU:
            self.handle_main_menu_key_press(key_name)
        elif current_state == GameState.NODE_SELECTION:
            self.handle_node_selection_key_press(key_name)
        elif current_state == GameState.COMBAT:
            self.handle_combat_key_press(key_name)
        elif current_state == GameState.EVENT:
            self.handle_event_key_press(key_name)
        elif current_state == GameState.DECK_VIEW:
            self.handle_deck_view_key_press(key_name)
        elif current_state == GameState.RELIC_VIEW:
            self.handle_relic_view_key_press(key_name)
        elif current_state == GameState.VICTORY_SCREEN:
            self.handle_victory_screen_key_press(key_name)

    def handle_mouse_click(self, pos):
        if self.state_machine.current_state == GameState.COMBAT:
            self.select_card(pos[0], pos[1])
            self.play_card()

    def render(self):
        if self.state_machine.current_state == GameState.MAIN_MENU:
            self.render_main_menu()
        elif self.state_machine.current_state == GameState.NODE_SELECTION:
            self.render_node_selection()
        elif self.state_machine.current_state == GameState.COMBAT:
            self.render_combat()
        elif self.state_machine.current_state == GameState.EVENT:
            self.render_event()
        elif self.state_machine.current_state == GameState.REST_SITE:
            self.render_rest_site()
        elif self.state_machine.current_state == GameState.TREASURE_ROOM:
            self.render_treasure_room()
        elif self.state_machine.current_state == GameState.VICTORY_SCREEN:
            self.render_victory_screen()
        elif self.state_machine.current_state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.state_machine.current_state == GameState.DECK_VIEW:
            self.render_deck_view()
        elif self.state_machine.current_state == GameState.RELIC_VIEW:
            self.render_relic_view()

        pygame.display.flip()

    def handle_main_menu(self):
        # TODO need to add keypresses for main menu
        if not self.player:
            if self.check_save_file():
                self.load_game()
            else:
                self.new_game()
            self.state_machine.transition_to(GameState.NODE_SELECTION)

    def handle_node_selection(self):
        available_nodes = [
            node for node in self.current_node.children if node is not None
        ]
        if not available_nodes:
            self.next_stage()
        else:
            self.state_machine.transition_to(GameState.NODE_SELECTION)

    def handle_combat(self):
        if not self.player_turn:
            self.execute_monster_turn()
        
        if self.player.health.value <= 0:
            self.state_machine.transition_to(GameState.GAME_OVER)
        elif not self.monster_group.monsters:
            self.handle_combat_victory()

    def handle_event(self):
        if self.current_event is None:
            self.initialize_event()
        # The actual event handling is done in handle_event_key_press

    def handle_rest_site(self):
        # Implement rest site logic
        # BUG
        # BUG Implement rest site logic
        self.state_machine.transition_to(GameState.NODE_SELECTION)

    def handle_treasure_room(self):
        # Implement treasure room logic
        
        self.state_machine.transition_to(GameState.NODE_SELECTION)

    def handle_victory_screen(self):
        # The actual victory screen handling is done in handle_victory_screen_key_press
        pass

    def handle_game_over(self):
        self.game_over_screen()
        self.reset_game_state()
        self.state_machine.transition_to(GameState.MAIN_MENU)

    def handle_deck_view(self):
        # The actual deck view handling is done in handle_deck_view_key_press
        pass

    def handle_relic_view(self):
        # The actual relic view handling is done in handle_relic_view_key_press
        pass

    def handle_main_menu_key_press(self, key_name):
        if key_name == "RETURN":
            self.state_machine.transition_to(GameState.NODE_SELECTION)

    def handle_node_selection_key_press(self, key_name):
        available_nodes = [
            node for node in self.current_node.children if node is not None
        ]
        if key_name in ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]:
            index = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"].index(key_name)
            if index < len(available_nodes):
                self.current_node = available_nodes[index]
                self.initialize_node()

    def handle_combat_key_press(self, key_name):
        if key_name == "SPACE":
            self.player_turn = False
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
            self.state_machine.transition_to(GameState.DECK_VIEW)
        elif key_name == "2":
            self.state_machine.transition_to(GameState.RELIC_VIEW)

    def handle_event_key_press(self, key_name):
        if key_name in ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]:
            index = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"].index(key_name)
            if index < len(self.current_event.options):
                self.text_event_selection = index
                self.handle_event_selection()

    def handle_deck_view_key_press(self, key_name):
        if key_name == "H":
            self.current_page = max(0, self.current_page - 1)
        elif key_name == "L":
            max_page = (len(self.player.get_sorted_full_deck()) - 1) // self.cards_per_page
            self.current_page = min(max_page, self.current_page + 1)
        elif key_name == "ESCAPE":
            self.state_machine.transition_to(GameState.COMBAT)

    def handle_relic_view_key_press(self, key_name):
        if key_name in ["ESCAPE", "2"]:
            self.state_machine.transition_to(GameState.COMBAT)

    def handle_victory_screen_key_press(self, key_name):
        if key_name in ["Q", "W", "E", "R"]:
            index = ["Q", "W", "E", "R"].index(key_name)
            new_cards = Card.generate_card_pool(3)
            if index < 3:
                self.player.add_card_to_deck(new_cards[index])
            else:
                self.player.increase_max_health(self.player.health_gain_on_skip)
            self.state_machine.transition_to(GameState.NODE_SELECTION)

    def render_main_menu(self):
        render_start_screen(self.screen, self.assets)

    def render_node_selection(self):
        available_nodes = [
            node for node in self.current_node.children if node is not None
        ]
        render_node_selection(
            self.screen,
            self.node_map,
            self.current_node,
            available_nodes,
            0,  # selected_index is not used in this implementation
            self.assets,
            self.player,
        )

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

    def render_rest_site(self):
        # BUG
        # BUG Implement rest site rendering
        pass

    def render_treasure_room(self):
        # Implement treasure room rendering
        pass

    def render_victory_screen(self):
        new_cards = Card.generate_card_pool(3)
        render_victory_state(
            self.screen, new_cards, -1, self.score, self.player, self.assets
        )

    def render_game_over(self):
        game_over_image = pygame.transform.scale(
            self.assets.game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.screen.blit(game_over_image, (0, 0))

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

    def render_relic_view(self):
        render_relic_view(self.screen, self.player.relics, self.assets)

    def new_game(self):
        self.player = Player.create("Hero", 100, "@")
        self.stage = 1
        self.score = 0
        self.player.reset_hand()
        self.generate_node_map()
        self.current_node = self.map_generator.get_start_node()
        self.initialize_combat()
        self.logger.info("New game started", category="SYSTEM")

    def generate_node_map(self):
        self.node_map = self.map_generator.generate_map()
        self.current_node = self.node_map[0][self.width // 2]
        self.logger.info(
            f"Node map generated with {sum(node is not None for row in self.node_map for node in row)} nodes"
        )
        self.map_generator.print_map()

    def select_card(self, mouse_x: int, mouse_y: int):
        card_start_x = (
            SCREEN_WIDTH
            - (len(self.player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)
        ) // 2
        for i in range(len(self.player.hand)):
            card_rect = pygame.Rect(
                card_start_x + i * (CARD_WIDTH + CARD_SPACING),
                SCREEN_HEIGHT - CARD_HEIGHT - 20,
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

            self.score += self.player.play_card(card, self.monster_group)
            self.logger.info(
                f"Player played card: {card.name} on {target_monster.name}",
                category="COMBAT",
            )
            self.selected_card = -1

    def execute_monster_turn(self):
        self.apply_relic_effects(TriggerWhen.END_OF_TURN)
        self.monster_group.remove_dead_monsters()

        for monster in self.monster_group.monsters:
            monster.status_effects.trigger_effects(TriggerType.TURN_START, monster)
            removed_monsters = self.monster_group.remove_dead_monsters()
            for removed_monster in removed_monsters:
                self.logger.debug(f"Removed monster: {removed_monster.name}", category="COMBAT")

        for i, monster in enumerate(self.monster_group.monsters):
            try:
                result = monster.execute_action(self.player)
                self.logger.debug(
                    f"Monster {i} {monster.name} executed action: {result}",
                    category="COMBAT",
                )
            except ValueError as e:
                self.logger.error(
                    f"Error executing monster action: {str(e)}", category="COMBAT"
                )

        try:
            self.monster_intentions = self.monster_group.decide_action(self.player)
            self.logger.debug(
                f"New monster intentions: {self.monster_intentions}",
                category="COMBAT",
            )
        except ValueError as e:
            self.logger.error(
                f"Error setting monster intentions: {str(e)}", category="COMBAT"
            )

        self.apply_relic_effects(TriggerWhen.ON_DAMAGE_TAKEN)
        self.player.end_turn()
        self.player_turn = True

        self.player.status_effects.trigger_effects(TriggerType.TURN_START, self.player)
        self.apply_relic_effects(TriggerWhen.START_OF_TURN)
        self.logger.debug("Turn ended, new turn started", category="COMBAT")

    def handle_combat_victory(self):
        self.player.end_turn()
        self.apply_relic_effects(TriggerWhen.END_OF_COMBAT)
        self.player.heal(self.player.hp_regain_per_level)
        self.player.reset_energy()
        self.player.status_effects.clear_effects()
        self.logger.info(
            f"Combat victory at node level: {self.current_node.y}",
            category="COMBAT",
        )
        self.player.increase_max_energy(1, self.current_node.y)

        victory_sequence = VictorySequence(self.screen, self.assets)
        victory_sequence.start()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state_machine.transition_to(GameState.GAME_OVER)
                    return
                elif event.type == pygame.KEYDOWN:
                    running = False

            self.render()
            running = victory_sequence.update()
            victory_sequence.render()
            pygame.display.flip()
            self.clock.tick(60)

        self.player.reset_hand()
        self.auto_save()

        if self.current_node.node_type == NodeType.BOSS:
            self.next_stage()
        else:
            self.select_next_node()

        self.state_machine.transition_to(GameState.VICTORY_SCREEN)

    def next_stage(self):
        self.stage += 1
        new_relic = self.relic_selection_screen(self.assets)
        if new_relic:
            self.logger.info(self.player.add_relic(new_relic), category="PLAYER")
            self.logger.info(f"New relic acquired: {new_relic.name}", category="PLAYER")

        self.node_map = self.map_generator.generate_map()
        self.current_node = self.node_map[0][self.width // 2]
        self.logger.info(f"Entered stage {self.stage}", category="SYSTEM")
        self.select_next_node()

    def select_next_node(self):
        available_nodes = [
            node for node in self.current_node.children if node is not None
        ]
        self.logger.debug(f"Available nodes: {len(available_nodes)}")
        if available_nodes:
            self.current_node = random.choice(available_nodes)
            self.logger.info(
                f"Selected node type: {self.current_node.node_type}", category="SYSTEM"
            )
            self.logger.debug(
                f"Node content: {self.current_node.content}", category="SYSTEM"
            )
            self.initialize_node()
        else:
            self.logger.warning("No available nodes, moving to next stage")
            self.next_stage()

    def initialize_node(self):
        self.logger.debug(f"Initializing node of type: {self.current_node.node_type}")
        if self.current_node.node_type in [NodeType.MONSTER, NodeType.ELITE, NodeType.BOSS]:
            self.initialize_combat()
            self.state_machine.transition_to(GameState.COMBAT)
        elif self.current_node.node_type == NodeType.EVENT:
            self.initialize_event()
            self.state_machine.transition_to(GameState.EVENT)
        elif self.current_node.node_type == NodeType.REST:
            self.state_machine.transition_to(GameState.REST_SITE)
        elif self.current_node.node_type == NodeType.TREASURE:
            self.state_machine.transition_to(GameState.TREASURE_ROOM)

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
        self.apply_relic_effects(TriggerWhen.START_OF_COMBAT)

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

    def relic_selection_screen(self, assets: GameAssets) -> Optional[Relic]:
        new_relics: List[Relic] = Relic.generate_relic_pool(3)
        selected_relic: int = -1
        running: bool = True

        while running:
            render_relic_selection(self.screen, new_relics, selected_relic, assets)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    num_keys = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]
                    for i, num_key in enumerate(num_keys):
                        if event.key == num_key:
                            if i < 3:
                                self.logger.info(
                                    f"Selected relic: {new_relics[i].name}",
                                    category="PLAYER",
                                )
                                return new_relics[i]
                            elif i == 3:
                                self.player.increase_max_health(
                                    self.player.health_gain_on_skip
                                )
                                self.logger.info(
                                    f"Skipped relic selection, increased max health by {self.player.health_gain_on_skip}",
                                    category="PLAYER",
                                )
                                return None

            pygame.time.wait(100)

        return None

    def reset_game_state(self):
        self.player = None
        self.monster_group = None
        self.current_node = None
        self.stage = 1
        self.score = 0
        self.selected_card = -1
        self.player_turn = True
        self.logger.info("Game state reset after game over", category="SYSTEM")

    def save_game(self):
        if self.node_map is None or self.current_node is None:
            self.logger.error(
                "Cannot save game: node_map or current_node is None", category="SYSTEM"
            )
            return

        save_data = {
            "player": self.player.to_dict(),
            "node_map": [
                [node.to_dict() if node else None for node in row]
                for row in self.node_map
            ],
            "current_node": {"x": self.current_node.x, "y": self.current_node.y},
            "stage": self.stage,
            "score": self.score,
            "game_over": self.state_machine.current_state == GameState.GAME_OVER,
        }
        try:
            with open("save_game.json", "w") as f:
                json.dump(save_data, f, cls=CustomJSONEncoder)
            self.logger.info("Game saved successfully", category="SYSTEM")
        except Exception as e:
            self.logger.error(
                f"Unexpected error during game save: {str(e)}", category="SYSTEM"
            )

    def load_game(self):
        try:
            with open("save_game.json", "r") as f:
                save_data = json.load(f)
            if save_data.get("game_over", False):
                self.logger.info(
                    "Previous game was over. Starting a new game.", category="SYSTEM"
                )
                self.new_game()
            else:
                self.player = Player.from_dict(save_data["player"])
                self.node_map = [
                    [None for _ in range(len(save_data["node_map"][0]))]
                    for _ in range(len(save_data["node_map"]))
                ]
                for y, row in enumerate(save_data["node_map"]):
                    for x, node_data in enumerate(row):
                        if node_data:
                            self.node_map[y][x] = Node.from_dict(node_data)
                
                # Second pass to set up children and parents
                for y, row in enumerate(save_data["node_map"]):
                    for x, node_data in enumerate(row):
                        if node_data:
                            self.node_map[y][x] = Node.from_dict(node_data, self.node_map)
                
                self.current_node = self.node_map[save_data["current_node"]["y"]][save_data["current_node"]["x"]]
                self.stage = save_data["stage"]
                self.score = save_data["score"]
                if self.current_node.node_type in [NodeType.MONSTER, NodeType.ELITE, NodeType.BOSS]:
                    self.monster_group = self.current_node.content["monsters"]
                elif self.current_node.node_type == NodeType.EVENT:
                    self.current_event = self.current_node.content["event"]
                self.logger.info("Game loaded successfully", category="SYSTEM")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading game: {e}", category="SYSTEM")
            self.logger.info("Starting a new game", category="SYSTEM")
            self.new_game()

    def get_node_path(self, root: List[List[Optional[Node]]], target: Node) -> List[int]:
        def dfs(node: Node, path: List[int]) -> Optional[List[int]]:
            if node == target:
                return path
            for i, child in enumerate(node.children):
                result = dfs(child, path + [i])
                if result:
                    return result
            return None

        for y, row in enumerate(root):
            for x, node in enumerate(row):
                if node:
                    path = dfs(node, [y, x])
                    if path:
                        return path
        return []

    def get_node_from_path(self, root: List[List[Optional[Node]]], path: List[int]) -> Node:
        node = root[path[0]][path[1]]
        for index in path[2:]:
            node = node.children[index]
        return node

    def auto_save(self):
        self.save_game()

    def check_save_file(self):
        return os.path.exists("save_game.json")

    def apply_relic_effects(self, trigger: TriggerWhen):
        msg = self.player.apply_relic_effects(trigger)
        if msg:
            self.logger.debug(msg, category="PLAYER")
        for relic in self.player.relics:
            if isinstance(relic, dict):
                relic_obj = Relic.from_dict(relic)
            elif isinstance(relic, Relic):
                relic_obj = relic
            else:
                self.logger.warning(f"Invalid relic type: {type(relic)}", category="SYSTEM")
                continue

            if relic_obj.trigger_when == trigger:
                effect_msg = relic_obj.apply_effect(self.player, self)
                self.logger.debug(f"Applied relic effect: {effect_msg}", category="PLAYER")

    def animate_combat_start(self):
        animation_duration = 1.0  # seconds
        start_time = time.time()

        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            progress = min(elapsed_time / animation_duration, 1.0)

            self.render_combat_with_animation(progress)

            if progress >= 1.0:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state_machine.transition_to(GameState.GAME_OVER)
                    return

            self.clock.tick(60)

    def render_combat_with_animation(self, animation_progress: float):
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
            animation_progress,
        )
        pygame.display.flip()

    def view_keybinds(self):
        render_keybinds(self.screen, self.assets)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state_machine.transition_to(GameState.GAME_OVER)
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
            self.clock.tick(30)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Deckdeep Deckbuilder")
    logger = GameLogger("deckdeep_logger", "deckdeep.log")
    game = Game(screen, logger)
    game.run()