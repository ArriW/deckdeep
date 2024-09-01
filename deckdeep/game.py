import pygame
import json
import os
import random
from typing import Optional, List, Tuple
from deckdeep.assets import GameAssets
from deckdeep.player import Player
from deckdeep.monster_group import MonsterGroup
from deckdeep.card import Card
from deckdeep.music_manager import BackgroundMusicManager
from deckdeep.render import (
    render_combat_state,
    render_victory_state,
    render_start_screen,
    render_game_over_screen,
    render_menu,
    render_text_event,
    render_node_selection,
    render_deck_view,
    render_relic_selection,
    render_relic_view,
)
from deckdeep.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_SPACING,
    scale,
)
from deckdeep.status_effect import Bleed, HealthRegain, EnergyBonus
from deckdeep.events import (
    Medic,
    Thrifter,
    CursedWell,
    Scribe,
    ForgottenShrine,
    get_random_event,
    VoodooDoctor,
    Defender,
    DarkMerchant,
    RestSite,
    Priest,
    AncientLibrary,
)
from deckdeep.relic import Relic, TriggerWhen
from deckdeep.config import (
    SCREEN_WIDTH,
    HEADER_HEIGHT,
    END_TURN_BUTTON_X,
    END_TURN_BUTTON_Y,
    VIEW_DECK_BUTTON_X,
    VIEW_DECK_BUTTON_Y,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
from time import sleep
from collections import Counter
from deckdeep.logger import GameLogger
from pygame.surface import Surface


class VictorySequence:
    def __init__(self, screen: Surface, assets: GameAssets):
        self.screen = screen
        self.assets = assets
        self.duration = 2000  # Duration in milliseconds
        self.start_time = 0
        self.particles: List[Tuple[int, int, int, int, float, float]] = (
            []
        )  # x, y, size, color, speed_x, speed_y

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


class Node:
    def __init__(
        self,
        node_type: str,
        stage: int,
        level: int,
        true_level: int,
        content: Optional[dict] = None,
    ):
        self.node_type = node_type
        self.stage = stage
        self.level = level
        self.true_level = true_level
        self.content = content or {}
        self.children: List[Node] = []

    def __str__(self) -> str:
        return f"Node({self.node_type}, {self.stage}, {self.level}, {self.true_level} )"

    def add_child(self, child: "Node"):
        self.children.append(child)

    def to_dict(self):
        content_dict = self.content.copy()
        if "monsters" in content_dict and isinstance(
            content_dict["monsters"], MonsterGroup
        ):
            content_dict["monsters"] = content_dict["monsters"].to_dict()
        if "event" in content_dict:
            content_dict["event"] = content_dict["event"].__class__.__name__
        return {
            "node_type": self.node_type,
            "stage": self.stage,
            "level": self.level,
            "true_level": self.true_level,
            "content": content_dict,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data):
        node = cls(
            data["node_type"],
            data["stage"],
            data["level"],
            data["true_level"],
            data["content"],
        )
        if "monsters" in node.content and isinstance(node.content["monsters"], dict):
            node.content["monsters"] = MonsterGroup.from_dict(node.content["monsters"])
        if "event" in node.content and isinstance(node.content["event"], str):
            event_class = globals()[node.content["event"]]
            node.content["event"] = event_class()
        for child_data in data["children"]:
            node.add_child(cls.from_dict(child_data))
        return node


class Game:
    def __init__(self, screen: pygame.Surface, logger: GameLogger):
        self.screen = screen
        self.logger = logger
        self.assets = GameAssets()
        self.player = Player("Hero", 100, "@")
        self.monster_group = MonsterGroup()
        self.current_node: Optional[Node] = None
        self.node_tree: Optional[Node] = None
        self.stage = 1
        self.score = 0
        self.selected_card = -1
        self.player_turn = True
        self.running = True
        self.clock = pygame.time.Clock()
        self.menu_active = False
        self.menu_options = ["Resume", "Save Game", "Load Game", "Quit"]
        self.menu_selected = 0
        self.game_over = False
        self.text_event_selection = 0
        self.deck_scroll = 0
        self.current_event = None
        # for deck view
        self.viewing_deck = False
        self.current_page = 0
        self.cards_per_page = 15  # 5 rows x 3 columns, as defined in render_deck_view
        # for relic view
        self.viewing_relics = False
        self.monster_intentions = []
        self.played_cards = []

    def run(self):
        while True:
            if not self.start_screen():
                return

            if self.check_save_file():
                self.load_game()
            else:
                self.new_game()

            with BackgroundMusicManager(self.assets.music_path) as music_manager:
                while self.running and not self.game_over:
                    self.handle_events(music_manager)
                    self.render()
                    self.update()
                    self.clock.tick(60)

            if self.game_over:
                self.game_over_screen()

    def start_screen(self) -> bool:
        render_start_screen(self.screen, self.assets)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    waiting = False
        return True

    def new_game(self):
        self.player = Player("Hero", 100, "@")
        self.stage = 1
        self.score = 0
        self.player.reset_hand()
        self.game_over = False
        self.generate_node_tree()
        self.current_node = self.node_tree
        self.monster_group = self.current_node.content[
            "monsters"
        ]  # pylint: # type: ignore
        self.initialize_combat()
        self.apply_relic_effects(TriggerWhen.START_OF_COMBAT)
        self.logger.info("New game started", category="SYSTEM")

    def generate_node_tree(self):
        root_level = (self.stage - 1) * 9 + 1
        monster_group, target_power, actual_power = MonsterGroup.generate(root_level)
        self.node_tree = Node(
            "combat", self.stage, 1, root_level, {"monsters": monster_group}
        )
        self.logger.info(
            f"Generated root node monster group: Target power: {target_power:.2f}, Actual power: {actual_power:.2f}",
            category="SYSTEM",
        )
        current_level = [self.node_tree]

        for level in range(2, 10):
            next_level = []
            for parent in current_level:
                num_children = random.randint(2, 3)
                for _ in range(num_children):
                    true_level = (self.stage - 1) * 9 + level

                    if level == 9:
                        monster_group, target_power, actual_power = (
                            MonsterGroup.generate(true_level, is_boss=True)
                        )
                        child = Node(
                            "boss",
                            self.stage,
                            level,
                            true_level,
                            {"monsters": monster_group},
                        )
                        self.logger.info(
                            f"Generated boss node monster group: Level {true_level}, Target power: {target_power:.2f}, Actual power: {actual_power:.2f}",
                            category="SYSTEM",
                        )
                    else:
                        node_type = random.choice(["combat", "event", "combat"])
                        if node_type == "combat":
                            monster_group, target_power, actual_power = (
                                MonsterGroup.generate(true_level)
                            )
                            content = {"monsters": monster_group}
                            
                            self.logger.info(
                                f"Generated combat node monster group: Level {true_level}, Target power: {target_power:.2f}, Actual power: {actual_power:.2f} , Delta: {round(actual_power-target_power)}",
                                category="SYSTEM",
                            )
                        else:
                            content = {"event": get_random_event()}
                        child = Node(node_type, self.stage, level, true_level, content)
                    parent.add_child(child)
                    next_level.append(child)
            current_level = next_level
        self.logger.info(
            f"Node tree generated for stage {self.stage}", category="SYSTEM"
        )

    def handle_events(self, music_manager: BackgroundMusicManager):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self.viewing_deck:
                    self.handle_deck_view_key_press(event.key)
                elif self.viewing_relics:
                    self.handle_relic_view_key_press(event.key)
                elif self.menu_active:
                    self.handle_menu_key_press(event.key)
                elif self.current_node.node_type == "event":
                    self.handle_event_key_press(event.key)
                else:
                    self.handle_key_press(event.key)
            music_manager.handle_event(event)

    def handle_mouse_click(self, pos):
        if not self.menu_active and not self.viewing_deck and not self.viewing_relics:
            mouse_x, mouse_y = pos
            self.select_card(mouse_x, mouse_y)
            self.check_end_turn_button(mouse_x, mouse_y)
            self.check_view_deck_button(mouse_x, mouse_y)

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

    def check_end_turn_button(self, mouse_x: int, mouse_y: int):
        end_turn_rect = pygame.Rect(
            END_TURN_BUTTON_X, END_TURN_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT
        )
        if end_turn_rect.collidepoint(mouse_x, mouse_y):
            self.player_turn = False
            self.logger.info("Player ended turn", category="PLAYER")

    def check_view_deck_button(self, mouse_x: int, mouse_y: int):
        view_deck_rect = pygame.Rect(
            VIEW_DECK_BUTTON_X, VIEW_DECK_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT
        )
        if view_deck_rect.collidepoint(mouse_x, mouse_y):
            self.viewing_deck = True
            self.deck_scroll = 0
            self.logger.debug("Viewing deck", category="PLAYER")

    def handle_key_press(self, key):
        if self.current_node.node_type in ["combat", "boss"]:
            self.handle_combat_key_press(key)
        elif self.current_node.node_type == "event":
            self.handle_event_key_press(key)

    def handle_combat_key_press(self, key):
        # num_keys = [
        #     pygame.K_1,
        #     pygame.K_2,
        #     pygame.K_3,
        #     pygame.K_4,
        #     pygame.K_5,
        #     pygame.K_6,
        #     pygame.K_7,
        #     pygame.K_8,
        #     pygame.K_9,
        #     pygame.K_0,
        # ]
        num_keys = [
            pygame.K_q,
            pygame.K_w,
            pygame.K_e,
            pygame.K_r,
            pygame.K_t,
            pygame.K_y,
            pygame.K_u,
            pygame.K_i,
            pygame.K_o,
            pygame.K_p,
        ]
        for i, num_key in enumerate(num_keys):
            if key == num_key and i < len(self.player.hand):
                self.selected_card = i
                self.play_card()
                break

        if key == pygame.K_SPACE:
            self.player_turn = False
            self.logger.info("Player ended turn", category="PLAYER")
        elif key == pygame.K_h:
            self.monster_group.select_previous()
            self.logger.debug("Selected previous monster", category="PLAYER")
        elif key == pygame.K_l:
            self.monster_group.select_next()
            self.logger.debug("Selected next monster", category="PLAYER")
        elif key == pygame.K_ESCAPE:
            self.logger.info("Opened Menu", category="SYSTEM")
            self.menu_active = True
        elif key == pygame.K_1:
            self.viewing_deck = True
            self.deck_scroll = 0
            self.logger.debug("Viewing deck", category="PLAYER")
        elif key == pygame.K_2:
            self.viewing_relics = True
            self.logger.debug("Viewing relics", category="PLAYER")

    def handle_event_key_press(self, key):
        # num_keys = [
        #     pygame.K_1,
        #     pygame.K_2,
        #     pygame.K_3,
        #     pygame.K_4,
        #     pygame.K_5,
        #     pygame.K_6,
        #     pygame.K_7,
        #     pygame.K_8,
        #     pygame.K_9,
        #     pygame.K_0,
        # ]
        num_keys = [
            pygame.K_q,
            pygame.K_w,
            pygame.K_e,
            pygame.K_r,
            pygame.K_t,
            pygame.K_y,
            pygame.K_u,
            pygame.K_i,
            pygame.K_o,
            pygame.K_p,
        ]
        for i, num_key in enumerate(num_keys):
            if key == num_key and i < len(self.current_event.options):
                self.text_event_selection = i
                self.handle_event_selection()
                break

        if key == pygame.K_ESCAPE:
            self.logger.info("Opened menu", category="SYSTEM")
            self.menu_active = True
        elif key == pygame.K_2:
            self.viewing_relics = True
            self.logger.debug("Viewing relics", category="PLAYER")

    def handle_deck_view_key_press(self, key):
        if key == pygame.K_ESCAPE:
            self.viewing_deck = False
            self.logger.debug("Closed deck view", category="PLAYER")
        elif key == pygame.K_h:
            self.current_page = max(0, self.current_page - 1)
            self.logger.debug(
                f"Moved to deck page {self.current_page}", category="PLAYER"
            )
        elif key == pygame.K_l:
            max_page = (
                len(self.player.get_sorted_full_deck()) - 1
            ) // self.cards_per_page
            self.current_page = min(max_page, self.current_page + 1)
            self.logger.debug(
                f"Moved to deck page {self.current_page}", category="PLAYER"
            )

    def handle_relic_view_key_press(self, key):
        if key == pygame.K_ESCAPE or key == pygame.K_2:
            self.viewing_relics = False
            self.logger.debug("Closed relic view", category="PLAYER")

    def handle_event_selection(self):
        option_text, option_method = self.current_event.options[
            self.text_event_selection
        ]
        result = self.current_event.execute_option(
            option_method, self.player, self.assets
        )
        for relic in self.player.relics:
            if relic.trigger_when == TriggerWhen.PERMANENT:
                msg = relic.apply_effect(self.player, self)
                self.logger.debug(msg, category="PLAYER")
        self.logger.info(f"Event option selected: {option_text}", category="EVENT")
        self.logger.info(f"Event result: {result}", category="EVENT")
        self.player.increase_max_energy(self.current_node.level)
        self.select_next_node()

    def handle_menu_key_press(self, key):
        if key == pygame.K_k:
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
        elif key == pygame.K_j:
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
        elif key == pygame.K_SPACE:
            self.execute_menu_option()
        elif key == pygame.K_ESCAPE:
            self.menu_active = False
            self.logger.debug("Closed menu", category="SYSTEM")

    def execute_menu_option(self):
        selected_option = self.menu_options[self.menu_selected]
        self.logger.info(f"Executed menu option: {selected_option}", category="SYSTEM")
        if selected_option == "Resume":
            self.menu_active = False
        elif selected_option == "Save Game":
            self.save_game()
        elif selected_option == "Load Game":
            self.load_game()
        elif selected_option == "Quit":
            self.running = False

    def play_card(self):
        if self.selected_card != -1:
            card = self.player.hand[self.selected_card]
            if self.player.can_play_card(card):
                self.score += self.player.play_card(card, self.monster_group)
                self.logger.info(f"Player played card: {card.name}", category="COMBAT")
                if card.energy_bonus > 0:
                    self.player.status_effects.add_effect(
                        EnergyBonus(card.energy_bonus)
                    )
                if card.health_regain > 0:
                    self.player.status_effects.add_effect(
                        HealthRegain(card.health_regain)
                    )
                self.selected_card = -1
                self.apply_relic_effects(TriggerWhen.ON_ATTACK)
                card.is_animating = True
                self.played_cards.append(card)
                
            else:
                self.logger.info(
                    f"Player tried to play card: {card.name} but didn't have enough energy",
                    category="COMBAT",
                )

    def update(self):
        if self.current_node.node_type in ["combat", "boss"]:
            self.update_combat()
        elif self.current_node.node_type == "event":
            self.update_event()

        if self.player.health <= 0:
            self.apply_relic_effects(TriggerWhen.ON_DEATH)
            if self.player.health <= 0:
                self.game_over = True
                self.logger.info("Game over", category="SYSTEM")
                self.auto_save()

    def update_combat(self):
        if not self.player_turn:
            self.apply_relic_effects(TriggerWhen.END_OF_TURN)
            self.player.apply_status_effects()
            self.monster_group.remove_dead_monsters()

            for monster in self.monster_group.monsters:
                monster.apply_status_effects()
                self.monster_group.remove_dead_monsters()
            # Execute previous intentions
            for i, monster in enumerate(self.monster_group.monsters):
                result = monster.execute_action(self.player)
                self.logger.debug(
                    f"Monster {i} {monster.name} executed action: {result}",
                    category="COMBAT",
                )

            # Set new intentions for the next turn
            self.monster_intentions = self.monster_group.decide_action(self.player)
            self.logger.debug(
                f"New monster intentions: {self.monster_intentions}", category="COMBAT"
            )

            self.apply_relic_effects(TriggerWhen.ON_DAMAGE_TAKEN)
            self.player.end_turn()
            self.player_turn = True
            self.apply_relic_effects(TriggerWhen.START_OF_TURN)
            self.logger.debug("Turn ended, new turn started", category="COMBAT")
        else:
            # It's the player's turn, so we don't need to do anything here
            pass

        self.monster_group.remove_dead_monsters()

        if not self.monster_group.monsters:
            self.player.end_turn()
            self.combat_victory()

        if all(not card.is_animating for card in self.played_cards):
            self.played_cards.clear()  # Clear played cards after all animations are complete

    # In the Game class, modify the combat_victory method:
    def combat_victory(self):
        self.apply_relic_effects(TriggerWhen.END_OF_COMBAT)
        self.player.heal(self.player.hp_regain_per_level)
        self.player.reset_energy()
        self.player.status_effects.clear_effects()
        self.logger.info(
            f"Combat victory at node level: {self.current_node.level}",
            category="COMBAT",
        )
        self.player.increase_max_energy(self.current_node.level)

        victory_sequence = VictorySequence(self.screen, self.assets)
        victory_sequence.start()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    running = False

            self.render()  # Render the current game state
            running = victory_sequence.update()
            victory_sequence.render()
            pygame.display.flip()
            self.clock.tick(60)

        new_card = self.victory_screen(self.assets)
        if new_card:
            self.player.add_card_to_deck(new_card)
            self.logger.info(
                f"New card added to deck: {new_card.name}", category="PLAYER"
            )

        self.player.reset_hand()
        self.auto_save()

        if self.current_node.node_type == "boss":
            self.next_stage()
        else:
            self.select_next_node()

    def update_event(self):
        if self.current_event is None:
            self.current_event = self.current_node.content["event"]
            self.text_event_selection = 0
            self.logger.info(
                f"Event started: {self.current_event.name}", category="EVENT"
            )

    def next_stage(self):
        self.stage += 1
        new_relic = self.relic_selection_screen(self.assets)
        if new_relic:
            self.player.add_relic(new_relic)
            self.logger.info(f"New relic acquired: {new_relic.name}", category="PLAYER")
        self.generate_node_tree()
        self.current_node = self.node_tree
        self.monster_group = self.current_node.content["monsters"]
        self.apply_relic_effects(TriggerWhen.START_OF_COMBAT)
        self.logger.info(f"Entered stage {self.stage}", category="SYSTEM")

    def render(self):
        if self.menu_active:
            render_menu(self.screen, self.menu_options, self.menu_selected, self.assets)
        elif self.viewing_deck:
            total_pages = (
                len(self.player.get_sorted_full_deck()) - 1
            ) // self.cards_per_page + 1
            self.current_page = render_deck_view(
                self.screen,
                self.player.get_sorted_full_deck(),
                self.current_page,
                total_pages,
                self.assets,
            )
        elif self.viewing_relics:
            render_relic_view(self.screen, self.player.relics, self.assets)
        elif self.current_node.node_type in ["combat", "boss"]:
            render_combat_state(
                self.screen,
                self.player,
                self.monster_group,
                f"{self.current_node.stage}:{self.current_node.level}",
                self.score,
                self.selected_card,
                self.assets,
                self.played_cards
            )
        elif self.current_node.node_type == "event":
            if self.current_event:
                render_text_event(
                    self.screen,
                    self.current_event.name,
                    [option[0] for option in self.current_event.options],
                    self.assets,
                    self.player,
                )
            else:
                self.logger.error(
                    "current_event is None in render method", category="SYSTEM"
                )

    def initialize_combat(self):
        self.monster_intentions = self.monster_group.decide_action(self.player)
        self.logger.debug(
            f"Initial monster intentions: {self.monster_intentions}", category="COMBAT"
        )
        self.player_turn = True
        self.apply_relic_effects(TriggerWhen.START_OF_COMBAT)

    def select_next_node(self):
        if self.current_node.children:
            selected = self.node_selection_screen()
            self.current_node = self.current_node.children[selected]
            self.logger.info(
                f"Selected node type: {self.current_node.node_type}", category="SYSTEM"
            )
            self.logger.debug(f"Node content: {self.current_node}", category="SYSTEM")
            if self.current_node.node_type in ["combat", "boss"]:
                self.monster_group = self.current_node.content["monsters"]
                self.logger.debug(
                    f"Monster group: Power {round(self.monster_group.get_power_rating())} {self.monster_group}",
                    category="COMBAT",
                )
                self.initialize_combat()
            elif self.current_node.node_type == "event":
                self.current_event = self.current_node.content["event"]
                self.text_event_selection = 0
        else:
            self.next_stage()

    def node_selection_screen(self) -> int:
        selected = -1
        running = True

        while running:
            render_node_selection(
                self.screen, self.current_node.children, selected, self.assets
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return 0
                elif event.type == pygame.KEYDOWN:
                    # num_keys = [
                        # pygame.K_1,
                        # pygame.K_2,
                        # pygame.K_3,
                        # pygame.K_4,
                        # pygame.K_5,
                        # pygame.K_6,
                        # pygame.K_7,
                        # pygame.K_8,
                        # pygame.K_9,
                        # pygame.K_0,
                    # ]
                    num_keys = [
                        pygame.K_q,
                        pygame.K_w,
                        pygame.K_e,
                        pygame.K_r,
                        pygame.K_t,
                        pygame.K_y,
                        pygame.K_u,
                        pygame.K_i,
                        pygame.K_o,
                        pygame.K_p,
                    ]
                    for i, num_key in enumerate(num_keys):
                        if event.key == num_key and i < len(self.current_node.children):
                            self.logger.info(f"Selected node {i}", category="PLAYER")
                            return i

            pygame.time.wait(100)

    def victory_screen(self, assets: GameAssets) -> Optional[Card]:
        new_cards = Card.generate_card_pool(3)
        selected_card = -1
        running = True

        while running:
            render_victory_state(
                self.screen,
                self.score,
                new_cards,
                selected_card,
                assets,
                player=self.player,
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    # num_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
                    num_keys = [pygame.K_q ,pygame.K_w, pygame.K_e, pygame.K_r]
                    for i, num_key in enumerate(num_keys):
                        if event.key == num_key:
                            if i < 3:
                                self.logger.info(
                                    f"Selected victory card: {new_cards[i].name}",
                                    category="PLAYER",
                                )
                                return new_cards[i]
                            elif i == 3:
                                self.player.increase_max_health(
                                    self.player.health_gain_on_skip
                                )
                                self.logger.info(
                                    f"Skipped card selection, increased max health by {self.player.health_gain_on_skip}",
                                    category="PLAYER",
                                )
                                return None

            pygame.time.wait(100)

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
                    # num_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
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

    def game_over_screen(self):
        render_game_over_screen(self.screen, self.score, self.assets)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    waiting = False
        self.logger.info(
            "Game over screen closed, starting new game", category="SYSTEM"
        )
        self.new_game()

    def save_game(self):
        save_data = {
            "player": self.player.to_dict(),
            "node_tree": self.node_tree.to_dict(),  # pylint: # type: ignore
            "current_node_path": self.get_node_path(
                self.node_tree, self.current_node
            ),  # pylint: # type: ignore
            "stage": self.stage,
            "score": self.score,
            "game_over": self.game_over,
        }
        with open("save_game.json", "w") as f:
            json.dump(save_data, f)
        self.logger.info("Game saved successfully", category="SYSTEM")

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
                self.node_tree = Node.from_dict(save_data["node_tree"])
                self.current_node = self.get_node_from_path(
                    self.node_tree, save_data["current_node_path"]
                )
                self.stage = save_data["stage"]
                self.score = save_data["score"]
                self.game_over = save_data.get("game_over", False)
                if self.current_node.node_type in ["combat", "boss"]:
                    self.monster_group = self.current_node.content["monsters"]
                elif self.current_node.node_type == "event":
                    self.current_event = self.current_node.content["event"]
                self.logger.info("Game loaded successfully", category="SYSTEM")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading game: {e}", category="SYSTEM")
            self.logger.info("Starting a new game", category="SYSTEM")
            self.new_game()

    def get_node_path(self, root: Node, target: Node) -> List[Node]:
        def dfs(node: Node, path: List[int]) -> Optional[List[int]]:
            if node == target:
                return path
            for i, child in enumerate(node.children):
                result = dfs(child, path + [i])
                if result:
                    return result
            return None

        return dfs(root, []) or []

    def get_node_from_path(self, root: Node, path: List[int]) -> Node:
        node = root
        for index in path:
            node = node.children[index]
        return node

    def auto_save(self):
        self.save_game()

    def check_save_file(self):
        return os.path.exists("save_game.json")

    def apply_relic_effects(self, trigger: TriggerWhen):
        for relic in self.player.relics:
            if isinstance(relic, dict):
                # If the relic is a dictionary (serialized data), create a Relic object
                relic_obj = Relic.from_dict(relic)
            elif isinstance(relic, Relic):
                # If it's already a Relic object, use it directly
                relic_obj = relic
            else:
                # If it's neither a dict nor a Relic object, skip it
                self.logger.warning(
                    f"Invalid relic type: {type(relic)}", category="SYSTEM"
                )
                continue

            if relic_obj.trigger_when == trigger:
                relic_obj.apply_effect(self.player, self)
                self.logger.debug(
                    f"Applied relic effect: {relic_obj.name}", category="PLAYER"
                )
