import pygame
from typing import List, Optional
from deckdeep.config import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, CARD_SPACING, ICON_SIZE, PLAYER_SIZE, scale
from deckdeep.config import WHITE, BLACK, GRAY, YELLOW, GREEN, BLUE, RED, BEIGE , PURPLE
from deckdeep.config import FONT, SMALL_FONT, CARD_FONT
from deckdeep.config import HEADER_HEIGHT, END_TURN_BUTTON_X, END_TURN_BUTTON_Y, VIEW_DECK_BUTTON_X, VIEW_DECK_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT
from deckdeep.player import Player
from deckdeep.monster_group import MonsterGroup
from deckdeep.card import Card
from deckdeep.assets import GameAssets
from deckdeep.relic import Relic
import random
from collections import defaultdict, Counter
from pygame import QUIT, KEYDOWN, K_ESCAPE, K_RETURN, K_BACKSPACE, K_UP, K_DOWN
from time import sleep

def render_text(screen: pygame.Surface, text: str, x: int, y: int, color=BLACK, font=FONT):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def render_text_with_background(screen: pygame.Surface, text: str, x: int, y: int, font, text_color=BLACK, background_color=WHITE):
    text_surface = font.render(text, True, text_color)
    background_surface = pygame.Surface(text_surface.get_size())
    background_surface.fill(background_color)
    screen.blit(background_surface, (x, y))
    screen.blit(text_surface, (x, y))

def render_card(screen: pygame.Surface, card: Card, x: int, y: int, is_selected: bool, assets: GameAssets, hotkey=None):
    def render_icon_and_text(icon, text, current_y):
        screen.blit(icon, (x + x_anchor, current_y))
        render_text(screen, text, x + x_offset, current_y + y_text_offset, font=CARD_FONT)
        return current_y + y_offset

    x_offset = ICON_SIZE + scale(16)
    x_anchor = scale(10)
    y_offset = ICON_SIZE
    y_text_offset = scale(5)

    screen.blit(assets.parchment_texture, (x, y))
    pygame.draw.rect(screen, YELLOW if is_selected else BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
    
    name_surface = CARD_FONT.render(card.name, True, BLACK)
    name_x = x + (CARD_WIDTH - name_surface.get_width()) // 2
    screen.blit(name_surface, (name_x, y + scale(10)))

    current_y = y + y_offset + scale(15)

    icon_map = {
        'damage': (assets.attack_icon, f"{card.damage}{' (AOE)' if card.targets_all else ''}"),
        'bonus_damage': (assets.dice_icon, f"{card.bonus_damage}"),
        'healing': (assets.heal_icon, f"{card.healing}"),
        'shield': (assets.shield_icon, f"{card.shield}"),
        'card_draw': (assets.draw_icon, f"{card.card_draw}"),
        'health_cost': (assets.health_cost, f"-{card.health_cost}"),
        'bleed': (assets.bleed_icon, f"{card.bleed}"),
        'energy_bonus': (assets.energy_bonus_icon, f"+{card.energy_bonus}"),
        'health_regain': (assets.health_regain_icon, f"+{card.health_regain}")
    }

    for attr, (icon, text) in icon_map.items():
        if getattr(card, attr, 0) > 0:
            current_y = render_icon_and_text(icon, text, current_y)

    energy_x = x + CARD_WIDTH - x_offset + ICON_SIZE
    energy_y = y + CARD_HEIGHT - ICON_SIZE 
    screen.blit(assets.energy_icon, (energy_x - x_offset, energy_y))
    render_text(screen, f"{card.energy_cost}", energy_x, energy_y + y_text_offset, font=CARD_FONT)

    if hotkey is not None:
        render_text(screen, f"#{hotkey}", x + x_anchor, y + CARD_HEIGHT - x_offset, font=CARD_FONT)

def render_button(screen: pygame.Surface, text: str, x: int, y: int, width: int, height: int):
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
    render_text(screen, text, x + scale(10), y + scale(10))

def render_health_bar(screen: pygame.Surface, x: int, y: int, width: int, height: int, current: int, maximum: int, color, shield=0):
    pygame.draw.rect(screen, BLACK, (x - scale(1), y - scale(1), width + scale(2), height + scale(2)))
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    current_width = int(width * (current / maximum))
    pygame.draw.rect(screen, color, (x, y, current_width, height))
    
    if shield > 0:
        shield_width = int(width * (shield / maximum))
        s = pygame.Surface((shield_width, height))
        s.set_alpha(128)
        s.fill(BLUE)
        screen.blit(s, (x + current_width - shield_width, y))
    
    health_text = f"{current}/{maximum}"
    if shield > 0:
        health_text += f" (+{shield})"
    text_x = x + (width - SMALL_FONT.size(health_text)[0]) // 2
    render_text(screen, health_text, text_x, y + scale(2), color=WHITE, font=SMALL_FONT)

def render_status_effects(screen: pygame.Surface, x: int, y: int, status_effects: dict, assets: GameAssets):
    icon_spacing = scale(30) 
    effect_icons = {
        "Bleed": (assets.bleed_icon, YELLOW),
        "HealthRegain": (assets.health_regain_icon, YELLOW),
        "EnergyBonus": (assets.energy_bonus_icon, YELLOW),
        "PlayerBonus": (assets.attack_icon, YELLOW),
        "Strength": (assets.strength_icon, YELLOW)
    }
    for effect_name, effect in status_effects.items():
        if effect_name in effect_icons:
            icon, color = effect_icons[effect_name]
            screen.blit(icon, (x, y))
            render_text(screen, str(effect.value), x+round(ICON_SIZE/2), y-round(ICON_SIZE/2), color=color, font=SMALL_FONT)
            x += icon_spacing

def render_player(screen: pygame.Surface, player: Player, assets: GameAssets):
    player_image = pygame.transform.scale(assets.player, (PLAYER_SIZE, PLAYER_SIZE))
    
    x = scale(120)
    y = SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2
    offset = random.randint(-player.shake, player.shake)
    
    # Render status effects above the player
    status_effects = player.status_effects.effects.copy()
    if player.bonus_damage > 0:
        status_effects["PlayerBonus"] = type('obj', (object,), {'value': player.bonus_damage})()
    if player.strength > 0:
        status_effects["Strength"] = type('obj', (object,), {'value': player.strength})()
    render_status_effects(screen, x, y - scale(30), status_effects, assets)
    
    # Render player image
    screen.blit(player_image, (x + offset, y + offset))
    
    # Render health bar below the player
    health_bar_width = PLAYER_SIZE
    health_bar_height = scale(20)
    render_health_bar(screen, x, y + PLAYER_SIZE + scale(10), health_bar_width, health_bar_height, player.health, player.max_health, GREEN, player.shield)
    
    # Render energy bar below the health bar
    render_health_bar(screen, x, y + PLAYER_SIZE + scale(35), health_bar_width, health_bar_height, player.energy, player.max_energy, BLUE)
    
    if player.shake > 0:
        player.shake -= 1

def render_monsters(screen: pygame.Surface, monster_group: MonsterGroup, assets: GameAssets):
    num_monsters = len(monster_group.monsters)
    start_x = SCREEN_WIDTH - scale(120) - PLAYER_SIZE * num_monsters - scale(50) * (num_monsters - 1)
    
    for i, monster in enumerate(monster_group.monsters):
        monster_image = pygame.transform.scale(GameAssets.load_and_scale_ui(monster.image_path, (PLAYER_SIZE, PLAYER_SIZE)), (PLAYER_SIZE, PLAYER_SIZE))
        x = start_x + i * (PLAYER_SIZE + scale(50))
        y = SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2
        offset = random.randint(-monster.shake, monster.shake)
        
        # Render status effects above the monster
        render_status_effects(screen, x, y - scale(30), monster.status_effects.effects, assets)
        
        # Render monster image
        screen.blit(monster_image, (x + offset, y + offset))
        
        # Render health bar below the monster
        health_bar_width = PLAYER_SIZE
        health_bar_height = scale(20)
        render_health_bar(screen, x, y + PLAYER_SIZE + scale(10), health_bar_width, health_bar_height, monster.health, monster.max_health, RED, monster.shields)
        
        # Render monster damage below the health bar
        damage_text = f"DMG: {monster.damage}"
        damage_x = x + (health_bar_width - SMALL_FONT.size(damage_text)[0]) // 2
        render_text(screen, damage_text, damage_x, y + PLAYER_SIZE + scale(35), color=RED, font=SMALL_FONT)
        
        if monster.shake > 0:
            monster.shake -= 1
        if monster.selected:
            pygame.draw.rect(screen, YELLOW, (x - scale(5), y - scale(5), PLAYER_SIZE + scale(10), PLAYER_SIZE + scale(10)), 3)

def render_combat_state(screen: pygame.Surface, player: Player, monster_group: MonsterGroup, dungeon_level: str, score: int, selected_card: int, assets: GameAssets):
    screen.blit(assets.background_image, (0, 0))
    
    # Render parchment texture at the top
    header_height = scale(50)
    parchment = pygame.transform.scale(assets.parchment_texture, (SCREEN_WIDTH, header_height))
    screen.blit(parchment, (0, 0))
    
    # Render score in the top left
    render_text(screen, f"Score: {score}", scale(10), scale(15), color=BLACK)
    
    # Render dungeon level in the top center
    level_text = f"Level: {dungeon_level}"
    level_width = FONT.size(level_text)[0]
    render_text(screen, level_text, (SCREEN_WIDTH - level_width) // 2, scale(15), color=BLACK)
    
    render_player(screen, player, assets)
    render_monsters(screen, monster_group, assets)
        
    s = pygame.Surface((SCREEN_WIDTH, CARD_HEIGHT + scale(40)))
    s.set_alpha(128)
    s.fill((100, 100, 100))
    screen.blit(s, (0, SCREEN_HEIGHT - CARD_HEIGHT - scale(40)))
    
    card_start_x = (SCREEN_WIDTH - (len(player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) // 2
    for i, card in enumerate(player.hand):
        render_card(screen, card, card_start_x + i * (CARD_WIDTH + CARD_SPACING), SCREEN_HEIGHT - CARD_HEIGHT - scale(20), i == selected_card, assets, hotkey=i+1)
    
    render_button(screen, "End Turn", END_TURN_BUTTON_X, END_TURN_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
    render_button(screen, "View Deck", VIEW_DECK_BUTTON_X, VIEW_DECK_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
    
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
    
    render_text(screen, "#4: Skip", scale(250) + 3 * (CARD_WIDTH + CARD_SPACING), scale(250), color=WHITE)
    
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
        render_text(screen, f"#{i+1}: {option}", menu_x + scale(20), menu_y + scale(20) + i * scale(50), color=text_color)
   
    pygame.display.flip()

def render_text_event(screen: pygame.Surface, text: str, options: List[str], assets: GameAssets):
    screen.blit(assets.background_image, (0, 0))
    
    text_box_width = scale(600)
    text_box_height = scale(200)
    text_box_x = (SCREEN_WIDTH - text_box_width) // 2
    text_box_y = scale(100)
    
    pygame.draw.rect(screen, BEIGE, (text_box_x, text_box_y, text_box_width, text_box_height))
    pygame.draw.rect(screen, BLACK, (text_box_x, text_box_y, text_box_width, text_box_height), 2)
    
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if FONT.size(test_line)[0] <= text_box_width - scale(40):
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    for i, line in enumerate(lines):
        render_text(screen, line, text_box_x + scale(20), text_box_y + scale(20) + i * scale(30))
    
    option_height = scale(50)
    option_spacing = scale(20)
    options_start_y = text_box_y + text_box_height + scale(50)
    
    for i, option in enumerate(options):
        option_y = options_start_y + i * (option_height + option_spacing)
        pygame.draw.rect(screen, GRAY, (text_box_x, option_y, text_box_width, option_height))
        pygame.draw.rect(screen, BLACK, (text_box_x, option_y, text_box_width, option_height), 2)
        render_text(screen, f"#{i+1}: {option}", text_box_x + scale(20), option_y + scale(10))
    
    pygame.display.flip()

def render_node_selection(screen: pygame.Surface, nodes: List['Node'], selected: int, assets: GameAssets):
    screen.blit(assets.background_image, (0, 0))
    
    render_text(screen, "Choose your next path:", SCREEN_WIDTH // 2 - scale(100), scale(50))
    
    node_width = scale(150)
    node_height = scale(100)
    node_spacing = scale(50)
    total_width = len(nodes) * node_width + (len(nodes) - 1) * node_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    
    for i, node in enumerate(nodes):
        node_x = start_x + i * (node_width + node_spacing)
        node_y = SCREEN_HEIGHT // 2 - node_height // 2
        
        color = YELLOW if i == selected else WHITE
        pygame.draw.rect(screen, color, (node_x, node_y, node_width, node_height))
        pygame.draw.rect(screen, BLACK, (node_x, node_y, node_width, node_height), 2)
        
        node_type_text = node.node_type.capitalize()
        render_text(screen, node_type_text, node_x + scale(10), node_y + scale(10))
        render_text(screen, f"Level {node.level}", node_x + scale(10), node_y + scale(50))
        render_text(screen, f"#{i+1}", node_x + scale(10), node_y + node_height - scale(30))
    
    render_text(screen, "Press number keys to select a path", SCREEN_WIDTH // 2 - scale(150), SCREEN_HEIGHT - scale(50))
    
    pygame.display.flip()

def render_deck_view(screen: pygame.Surface, deck: List[Card], current_page: int, total_pages: int, assets: GameAssets):
    screen.blit(assets.background_image, (0, 0))
    
    render_text(screen, "Full Deck View", SCREEN_WIDTH // 2 - scale(50), scale(20))
    render_text(screen, f"Total Cards: {len(deck)}", SCREEN_WIDTH - scale(150), scale(20))
    render_text(screen, "Use Left/Right arrows to change pages, Esc to close", SCREEN_WIDTH // 2 - scale(200), SCREEN_HEIGHT - scale(30))
    
    cards_per_row = 5
    cards_per_column = 3
    cards_per_page = cards_per_row * cards_per_column
    card_spacing_x = scale(20)
    card_spacing_y = scale(20)
    start_x = (SCREEN_WIDTH - (cards_per_row * CARD_WIDTH + (cards_per_row - 1) * card_spacing_x)) // 2
    start_y = scale(80)
    
    current_page = max(0, min(current_page, total_pages - 1))
    
    start_index = current_page * cards_per_page
    end_index = min(start_index + cards_per_page, len(deck))
    
    for i, card in enumerate(deck[start_index:end_index]):
        row = i // cards_per_row
        col = i % cards_per_row
        x = start_x + col * (CARD_WIDTH + card_spacing_x)
        y = start_y + row * (CARD_HEIGHT + card_spacing_y)
        
        render_card(screen, card, x, y, False, assets)
    
    # Render page information
    render_text(screen, f"Page {current_page + 1} of {total_pages}", SCREEN_WIDTH // 2 - scale(50), SCREEN_HEIGHT - scale(60))
    
    pygame.display.flip()
    
    return current_page

def render_relic_selection(screen: pygame.Surface, new_relics: List[Relic], selected_relic: int, assets: GameAssets):
    screen.fill(BLACK)
    header_height = scale(200)
    s = pygame.Surface((SCREEN_WIDTH, header_height))
    s.set_alpha(128)
    s.fill(BEIGE)
    screen.blit(s, (0, 0))
    
    render_text(screen, "Select a Relic", SCREEN_WIDTH // 2 - scale(50), scale(50))
    render_text(screen, "Press number keys to select a relic, or SPACE to skip", SCREEN_WIDTH // 2 - scale(250), scale(100))
    
    relic_width = scale(200)
    relic_height = scale(150)
    relic_spacing = scale(50)
    total_width = len(new_relics) * relic_width + (len(new_relics) - 1) * relic_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    start_y = scale(250)
    
    for i, relic in enumerate(new_relics):
        relic_x = start_x + i * (relic_width + relic_spacing)
        relic_y = start_y
        
        color = YELLOW if i == selected_relic else WHITE
        pygame.draw.rect(screen, color, (relic_x, relic_y, relic_width, relic_height))
        pygame.draw.rect(screen, BLACK, (relic_x, relic_y, relic_width, relic_height), 2)
        
        render_text(screen, relic.name, relic_x + scale(10), relic_y + scale(10), font=SMALL_FONT)
        
        words = relic.description.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if SMALL_FONT.size(test_line)[0] <= relic_width - scale(20):
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        for j, line in enumerate(lines):
            render_text(screen, line, relic_x + scale(10), relic_y + scale(40) + j * scale(20), font=SMALL_FONT)
        
        render_text(screen, f"#{i+1}", relic_x + relic_width - scale(30), relic_y + relic_height - scale(30), font=SMALL_FONT)
    
    render_text(screen, "#4: Skip", start_x + 3 * (relic_width + relic_spacing), start_y, font=SMALL_FONT)
    
    pygame.display.flip()

def render_relic_view(screen: pygame.Surface, relics: List[Relic], assets: GameAssets):
    screen.blit(assets.background_image, (0, 0))
    
    render_text(screen, "Relic View", SCREEN_WIDTH // 2 - scale(50), scale(20))
    render_text(screen, f"Total Relics: {len(relics)}", SCREEN_WIDTH - scale(150), scale(20))
    render_text(screen, "Press Esc or R to close", SCREEN_WIDTH // 2 - scale(100), SCREEN_HEIGHT - scale(30))
    
    relic_width = scale(200)
    relic_height = scale(150)
    relic_spacing_x = scale(20)
    relic_spacing_y = scale(20)
    relics_per_row = 4
    start_x = (SCREEN_WIDTH - (relics_per_row * relic_width + (relics_per_row - 1) * relic_spacing_x)) // 2
    start_y = scale(80)
    
    relic_counts = Counter(relic.name for relic in relics)
    
    for i, (relic_name, count) in enumerate(relic_counts.items()):
        row = i // relics_per_row
        col = i % relics_per_row
        x = start_x + col * (relic_width + relic_spacing_x)
        y = start_y + row * (relic_height + relic_spacing_y)
        
        relic = next(relic for relic in relics if relic.name == relic_name)
        
        pygame.draw.rect(screen, WHITE, (x, y, relic_width, relic_height))
        pygame.draw.rect(screen, BLACK, (x, y, relic_width, relic_height), 2)
        
        render_text(screen, relic.name, x + scale(10), y + scale(10), font=SMALL_FONT)
        render_text(screen, f"Count: {count}", x + scale(10), y + scale(30), font=SMALL_FONT)
        
        words = relic.description.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if SMALL_FONT.size(test_line)[0] <= relic_width - scale(20):
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        for j, line in enumerate(lines):
            render_text(screen, line, x + scale(10), y + scale(50) + j * scale(20), font=SMALL_FONT)
    
    pygame.display.flip()

def handle_card_selection(full_deck: List[Card], assets: GameAssets):
    selected_index = 0
    clock = pygame.time.Clock()
    screen = pygame.display.get_surface()
    
    while True:
        render_card_selection(screen, sorted(full_deck, key=lambda card: (card.energy_cost, card.name)), selected_index, assets)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    selected_index = max(0, selected_index - 1)
                elif event.key == pygame.K_DOWN:
                    selected_index = min(len(full_deck) - 1, selected_index + 1)
                elif event.key == pygame.K_RETURN:
                    return selected_index
        
        clock.tick(30)

def render_card_selection(screen: pygame.Surface, full_deck: List[Card], selected_index: int, assets: GameAssets):
    screen.blit(assets.background_image, (0, 0))

    # Render parchment texture at the top
    header_height = scale(50)
    parchment = pygame.transform.scale(assets.parchment_texture, (SCREEN_WIDTH, header_height))
    screen.blit(parchment, (0, 0))

    render_text(screen, "Choose a card to remove:", scale(20), scale(15), color=BLACK)

    card_list_width = scale(400)
    card_list_height = SCREEN_HEIGHT - header_height - scale(60)
    card_list_x = scale(20)
    card_list_y = header_height + scale(20)

    pygame.draw.rect(screen, BEIGE, (card_list_x, card_list_y, card_list_width, card_list_height))
    pygame.draw.rect(screen, BLACK, (card_list_x, card_list_y, card_list_width, card_list_height), 2)

    visible_cards = 20 
    start_index = max(0, min(selected_index, len(full_deck) - visible_cards))

    for i, card in enumerate(full_deck[start_index:start_index + visible_cards]):
        color = RED if i + start_index == selected_index else BLACK
        card_text = f"{i + start_index + 1}: {card.name} (Energy: {card.energy_cost})"
        render_text(screen, card_text, card_list_x + scale(10), card_list_y + scale(10) + i * scale(30), color=color, font=SMALL_FONT)

    # Render selected card on the right
    if 0 <= selected_index < len(full_deck):
        selected_card = full_deck[selected_index]
        render_card(screen, selected_card, SCREEN_WIDTH - CARD_WIDTH - scale(40), header_height + scale(20), True, assets)

    instructions = "Use UP/DOWN arrows to navigate, ENTER to select, ESC to cancel"
    render_text(screen, instructions, scale(20), SCREEN_HEIGHT - scale(30), color=BLACK, font=SMALL_FONT)
    pygame.display.flip()