import pygame
from typing import List, Optional
from deckdeep.config import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, CARD_SPACING, ICON_SIZE, PLAYER_SIZE, scale
from deckdeep.config import WHITE, BLACK, GRAY, YELLOW, GREEN, BLUE, RED, BEIGE
from deckdeep.config import FONT, SMALL_FONT, CARD_FONT
from deckdeep.player import Player
from deckdeep.monster_group import MonsterGroup
from deckdeep.card import Card
from deckdeep.assets import GameAssets
import random

def render_text(screen: pygame.Surface, text: str, x: int, y: int, color=BLACK, font=FONT):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def render_card(screen: pygame.Surface, card: Card, x: int, y: int, is_selected: bool, assets: GameAssets, hotkey=None):
    x_offset = ICON_SIZE + scale(16)
    x_anchor = scale(10)
    y_offset = ICON_SIZE
    y_text_offset = scale(5)

    screen.blit(assets.parchment_texture, (x, y))

    border_color = YELLOW if is_selected else BLACK
    pygame.draw.rect(screen, border_color, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
    
    name_surface = CARD_FONT.render(card.name, True, BLACK)
    name_x = x + (CARD_WIDTH - name_surface.get_width()) // 2
    screen.blit(name_surface, (name_x, y + scale(10)))

    current_y = y + y_offset + scale(15)

    if card.damage > 0:
        attack_text = f"{card.damage}"
        if card.targets_all:
            attack_text += " (AOE)"
        screen.blit(assets.attack_icon, (x + x_anchor, current_y))
        render_text(screen, attack_text, x + x_offset, current_y + y_text_offset, font=CARD_FONT)
        current_y += y_offset 

    if card.bonus_damage > 0:
        screen.blit(assets.dice_icon, (x + x_anchor, current_y))
        render_text(screen, f"{card.bonus_damage}", x + x_offset, current_y + y_text_offset, font=CARD_FONT)
        current_y += y_offset 

    if card.healing > 0:
        screen.blit(assets.heal_icon, (x + x_anchor, current_y))
        render_text(screen, f"{card.healing}", x + x_offset, current_y + y_text_offset, font=CARD_FONT)
        current_y += y_offset 

    if card.shield > 0:
        screen.blit(assets.shield_icon, (x + x_anchor, current_y))
        render_text(screen, f"{card.shield}", x + x_offset, current_y + y_text_offset, font=CARD_FONT)
        current_y += y_offset

    if card.card_draw> 0:
        screen.blit(assets.draw_icon, (x + x_anchor, current_y))
        render_text(screen, f"{card.card_draw}", x + x_offset, current_y + y_text_offset, font=CARD_FONT)
        current_y += y_offset

    if card.health_cost> 0:
        screen.blit(assets.health_cost, (x + x_anchor, current_y))
        render_text(screen, f"-{card.health_cost}", x + x_offset, current_y + y_text_offset, font=CARD_FONT)
        current_y += y_offset


    energy_x = x + CARD_WIDTH - x_offset + ICON_SIZE
    energy_y = y + CARD_HEIGHT - ICON_SIZE 
    screen.blit(assets.energy_icon, (energy_x - x_offset, energy_y))
    render_text(screen, f"{card.energy_cost}", energy_x, energy_y + y_text_offset, font=CARD_FONT)

    if hotkey:
        render_text(screen, str(hotkey), x + x_anchor, y + CARD_HEIGHT - x_offset, font=CARD_FONT)

def render_button(screen: pygame.Surface, text: str, x: int, y: int, width: int, height: int):
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
    render_text(screen, text, x + scale(10), y + scale(10))

def render_health_bar(screen: pygame.Surface, x: int, y: int, width: int, height: int, current: int, maximum: int, color, name=None):
    pygame.draw.rect(screen, BLACK, (x - scale(1), y - scale(1), width + scale(2), height + scale(2)))
    pygame.draw.rect(screen, color, (x, y, int(width * (current / maximum)), height))
    if name:
        render_text(screen, name, x + scale(5), y + scale(2), color=WHITE, font=SMALL_FONT)

def render_player(screen: pygame.Surface, player: Player, assets: GameAssets):
    offset = random.randint(-player.shake, player.shake)
    screen.blit(assets.player, (scale(120) + offset, scale(250) + offset))
    if player.shake > 0:
        player.shake -= 1

def render_monsters(screen: pygame.Surface, monster_group: MonsterGroup):
    num_monsters = len(monster_group.monsters)
    start_x = scale(575) - (num_monsters - 1) * scale(50)
    for i, monster in enumerate(monster_group.monsters):
        offset = random.randint(-monster.shake, monster.shake)
        screen.blit(GameAssets.load_and_scale(monster.image_path,(PLAYER_SIZE,PLAYER_SIZE)), (start_x + i * scale(100) + offset, scale(250) + offset))
        if monster.shake > 0:
            monster.shake -= 1
        if monster.selected:
            pygame.draw.rect(screen, YELLOW, (start_x + i * scale(100) - scale(5), scale(245), scale(110), scale(110)), 3)

def render_combat_state(screen: pygame.Surface, player: Player, monster_group: MonsterGroup, dungeon_level: int, score: int, selected_card: int, assets: GameAssets):
    screen.blit(assets.background_image, (0, 0))
    
    header_height = scale(100)
    s = pygame.Surface((SCREEN_WIDTH, header_height))
    s.set_alpha(128)
    s.fill(BEIGE)
    screen.blit(s, (0, 0))
    
    render_text(screen, f"Dungeon Level: {dungeon_level}", scale(10), scale(10))
    render_text(screen, f"Score: {score}", scale(10), scale(40))
    render_text(screen, f"Player Bonus: {player.bonus_damage}", scale(10), scale(70))
    
    render_health_bar(screen, scale(200), scale(10), scale(200), scale(20), player.health, player.max_health, GREEN, "Player")
    render_text(screen, f"{player.health}/{player.max_health}", scale(405), scale(10))
    
    if player.shield > 0:
        shield_width = int(scale(200) * (player.shield / player.max_health))
        s = pygame.Surface((shield_width, scale(20)))
        s.set_alpha(128)
        s.fill(BLUE)
        screen.blit(s, (scale(400) - shield_width, scale(10)))
        render_text(screen, f"+{player.shield}", scale(405) - shield_width, scale(10), color=WHITE, font=SMALL_FONT)
    
    render_health_bar(screen, scale(200), scale(40), scale(200), scale(20), player.energy, player.max_energy, BLUE, "Energy")
    render_text(screen, f"{player.energy}/{player.max_energy}", scale(405), scale(40))
    
    for i, monster in enumerate(monster_group.monsters):
        y_offset = i * scale(30)
        render_health_bar(screen, scale(500), scale(10) + y_offset, scale(200), scale(20), monster.health, monster.max_health, RED, monster.name)
        screen.blit(assets.attack_icon, (scale(710), scale(8) + y_offset))
        render_text(screen, f"{monster.damage}", scale(735), scale(10) + y_offset, font=SMALL_FONT)
    
    render_player(screen, player, assets)
    render_monsters(screen, monster_group)
        
    s = pygame.Surface((SCREEN_WIDTH, CARD_HEIGHT + scale(40)))
    s.set_alpha(128)
    s.fill((100, 100, 100))
    screen.blit(s, (0, SCREEN_HEIGHT - CARD_HEIGHT - scale(40)))
    
    card_start_x = (SCREEN_WIDTH - (len(player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) // 2
    for i, card in enumerate(player.hand):
        render_card(screen, card, card_start_x + i * (CARD_WIDTH + CARD_SPACING), SCREEN_HEIGHT - CARD_HEIGHT - scale(20), i == selected_card, assets, hotkey=i+1)
    
    render_button(screen, "End Turn", SCREEN_WIDTH - scale(120), header_height + scale(10), scale(100), scale(40))
    render_button(screen, "Discard", SCREEN_WIDTH - scale(120), header_height + scale(60), scale(100), scale(40))
    
    pygame.display.flip()

def render_victory_state(screen: pygame.Surface, score: int, new_cards: List[Card], selected_card: int, assets: GameAssets):
    screen.fill(BLACK)
    header_height = scale(200)
    s = pygame.Surface((SCREEN_WIDTH, header_height))
    s.set_alpha(128)
    s.fill(BEIGE)
    screen.blit(s, (0, 0))
    
    render_text(screen, "Victory!", SCREEN_WIDTH // 2 - 50, 50)
    render_text(screen, f"Score: {score}", SCREEN_WIDTH // 2 - 50, 100)
    render_text(screen, "Select a card to add to your deck:", SCREEN_WIDTH // 2 - 150, 150)
    render_text(screen, "Press number keys to select a card, or SPACE to skip", SCREEN_WIDTH // 2 - 250, 175)
    
    for i, card in enumerate(new_cards):
        render_card(screen, card, scale(250) + i * (CARD_WIDTH + CARD_SPACING), scale(250), i == selected_card, assets, hotkey=i+1)
    
    pygame.display.flip()

def render_start_screen(screen: pygame.Surface, assets: GameAssets):
    screen.blit(assets.start_screen_image, (0, 0))
    render_text(screen, "Press any key to start", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50)
    pygame.display.flip()

def render_game_over_screen(screen: pygame.Surface, score: int, assets: GameAssets):
    screen.blit(assets.game_over_image, (0, 0))
    render_text(screen, f"Final Score: {score}", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 100)
    render_text(screen, "Press any key to continue", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50)
    pygame.display.flip()

def render_menu(screen: pygame.Surface, options: List[str], selected: int, assets: GameAssets):
   screen.blit(assets.background_image, (0, 0))
   
   menu_width = scale(300)
   menu_height = scale(50) * len(options) + scale(20)
   menu_x = (SCREEN_WIDTH - menu_width) // 2
   menu_y = (SCREEN_HEIGHT - menu_height) // 2
   
   pygame.draw.rect(screen, BEIGE, (menu_x, menu_y, menu_width, menu_height))
   pygame.draw.rect(screen, BLACK, (menu_x, menu_y, menu_width, menu_height), 2)
   
   for i, option in enumerate(options):
       text_color = YELLOW if i == selected else BLACK
       render_text(screen, option, menu_x + scale(20), menu_y + scale(20) + i * scale(50), color=text_color)
   
   pygame.display.flip()