import pygame
import json
import os
from typing import Optional
from deckdeep.assets import GameAssets
from deckdeep.player import Player
from deckdeep.monster_group import MonsterGroup
from deckdeep.card import Card
from deckdeep.music_manager import BackgroundMusicManager
from deckdeep.render import render_combat_state, render_victory_state, render_start_screen, render_game_over_screen, render_menu
from deckdeep.config import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT , CARD_SPACING, scale

class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.assets = GameAssets()
        self.player = Player("Hero", 100, '@')
        self.monster_group = MonsterGroup()
        self.dungeon_level = 1
        self.score = 0
        self.stages_cleared = 0
        self.selected_card = -1
        self.player_turn = True
        self.running = True
        self.clock = pygame.time.Clock()
        self.menu_active = False
        self.menu_options = ["Resume", "Save Game", "Load Game", "Quit"]
        self.menu_selected = 0
        self.game_over = False

    def run(self):
        if not self.start_screen():
            return

        # Check for existing save file and load it if it exists
        if self.check_save_file():
            self.load_game()
        else:
            self.new_game()

        with BackgroundMusicManager(self.assets.music_path) as music_manager:
            while self.running and not self.game_over:
                # handles user inputs until player turn is ended
                self.handle_events(music_manager)
                self.render()
                #  - handles monster actions when not players turn
                #  - clears dead monsters regardless of whose turn
                #  - Goes to victory screen if combat is not running
                #  - and then handles the updates with next level
                #       -  next level goes into a new render and the victory screen
                #          which temporarily controls render and control
                self.update()
                self.clock.tick(60)

        if self.game_over:
            self.game_over_screen()

    def new_game(self):
        self.player = Player("Hero", 100, '@')
        self.monster_group = MonsterGroup.generate(self.dungeon_level)
        self.dungeon_level = 1
        self.score = 0
        self.stages_cleared = 0
        self.player.reset_hand()
        self.game_over = False

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

    def handle_events(self, music_manager: BackgroundMusicManager):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self.menu_active:
                    self.handle_menu_key_press(event.key)
                else:
                    self.handle_key_press(event.key)
            music_manager.handle_event(event)

    def handle_mouse_click(self, pos):
        if not self.menu_active:
            mouse_x, mouse_y = pos
            self.select_card(mouse_x, mouse_y)
            self.check_end_turn_button(mouse_x, mouse_y)
            self.check_discard_button(mouse_x, mouse_y)

    def select_card(self, mouse_x: int, mouse_y: int):
        card_start_x = (SCREEN_WIDTH - (len(self.player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) // 2
        for i in range(len(self.player.hand)):
            card_rect = pygame.Rect(card_start_x + i * (CARD_WIDTH + CARD_SPACING), SCREEN_HEIGHT - CARD_HEIGHT - 20, CARD_WIDTH, CARD_HEIGHT)
            if card_rect.collidepoint(mouse_x, mouse_y):
                self.selected_card = i
                break

    def check_end_turn_button(self, mouse_x: int, mouse_y: int):
        end_turn_rect = pygame.Rect(SCREEN_WIDTH - scale(120), scale(110), scale(100), scale(40))
        if end_turn_rect.collidepoint(mouse_x, mouse_y):
            self.player_turn = False

    def check_discard_button(self, mouse_x: int, mouse_y: int):
        discard_rect = pygame.Rect(SCREEN_WIDTH - scale(120), scale(160), scale(100), scale(40))
        if discard_rect.collidepoint(mouse_x, mouse_y) and self.selected_card != -1:
            self.player.discard_card(self.selected_card)
            self.selected_card = -1

    def handle_key_press(self, key):
        num_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
        for i, num_key in enumerate(num_keys):
            if key == num_key and i < len(self.player.hand):
                self.selected_card = i
                self.play_card()
                break

        if key == pygame.K_e:
            self.player_turn = False
        elif key == pygame.K_UP:
            self.monster_group.select_previous()
        elif key == pygame.K_DOWN:
            self.monster_group.select_next()
        elif key == pygame.K_ESCAPE:
            print("open menu")
            self.menu_active = True

    def handle_menu_key_press(self, key):
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN:
            self.execute_menu_option()
        elif key == pygame.K_ESCAPE:
            self.menu_active = False

    def execute_menu_option(self):
        if self.menu_options[self.menu_selected] == "Resume":
            self.menu_active = False
        elif self.menu_options[self.menu_selected] == "Save Game":
            self.save_game()
        elif self.menu_options[self.menu_selected] == "Load Game":
            self.load_game()
        elif self.menu_options[self.menu_selected] == "Quit":
            self.running = False

    def play_card(self):
        if self.selected_card != -1:
            card = self.player.hand[self.selected_card]
            if self.player.can_play_card(card):
                self.score += self.player.play_card(card, self.monster_group)
                self.selected_card = -1

    def update(self):
        if not self.player_turn:
            self.monster_group.attack(self.player)
            self.player.end_turn()
            self.player_turn = True

        self.monster_group.remove_dead_monsters()

        if self.player.health <= 0:
            self.game_over = True
            self.auto_save() 
        elif not self.monster_group.monsters:
            self.next_level()

    def next_level(self):
        self.dungeon_level += 1
        self.stages_cleared += 1
        self.player.heal(self.player.hp_regain_per_level)
        self.player.reset_energy()

        if self.stages_cleared % 3 == 0 and self.player.max_energy < 10:
            self.player.increase_max_energy()
            self.player.energy += 1

        new_card = self.victory_screen(assets=self.assets)
        if new_card:
            self.player.add_card_to_deck(new_card)

        self.monster_group = MonsterGroup.generate(self.dungeon_level)
        self.player.reset_hand()

        # Auto-save after completing a level
        self.auto_save()

    def victory_screen(self,assets: GameAssets) -> Optional[Card]:
        new_cards = Card.generate_card_pool(3)
        selected_card = 0
        running = True

        while running:
            render_victory_state(self.screen, self.score, new_cards, selected_card, assets)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        selected_card = event.key - pygame.K_1
                        return new_cards[selected_card]
                    elif event.key == pygame.K_SPACE:
                        self.player.increase_max_health(self.player.health_gain_on_skip)
                        return None

            pygame.time.wait(100)

    def render(self):
        if self.menu_active:
            render_menu(self.screen, self.menu_options, self.menu_selected, self.assets)
        else:
            render_combat_state(self.screen, self.player, self.monster_group, self.dungeon_level, self.score, self.selected_card, self.assets)

    def game_over_screen(self):
        render_game_over_screen(self.screen, self.score, self.assets)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    waiting = False
        self.new_game()  # Start a new game after game over screen

    def save_game(self):
        save_data = {
            "player": self.player.to_dict(),
            "monster_group": self.monster_group.to_dict(),
            "dungeon_level": self.dungeon_level,
            "score": self.score,
            "stages_cleared": self.stages_cleared,
            "game_over": self.game_over,
        }
        with open("save_game.json", "w") as f:
            json.dump(save_data, f)
        print("Game saved successfully!")

    def load_game(self):
        try:
            with open("save_game.json", "r") as f:
                save_data = json.load(f)
            if save_data.get("game_over", False):
                print("Previous game was over. Starting a new game.")
                self.new_game()
            else:
                self.player = Player.from_dict(save_data["player"])
                self.monster_group = MonsterGroup.from_dict(save_data["monster_group"])
                self.dungeon_level = save_data["dungeon_level"]
                self.score = save_data["score"]
                self.stages_cleared = save_data["stages_cleared"]
                self.game_over = save_data.get("game_over", False)
                print("Game loaded successfully!")
        except FileNotFoundError:
            print("No saved game found. Starting a new game.")
            self.new_game()

    def auto_save(self):
        self.save_game()

    def check_save_file(self):
        return os.path.exists("save_game.json")

