import pygame
from pathlib import Path
import random
import colorsys
from typing import List

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_WIDTH = 120
CARD_HEIGHT = 180
CARD_SPACING = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BEIGE = (245, 245, 220)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("D&D Deckbuilder")

# Load fonts
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)
card_font = pygame.font.Font(None, 20)

# Load background image
background_image = pygame.image.load("./images/background.png")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load SVG icons
icon_size = 24
attack_icon = pygame.image.load("./images/attack.svg")
attack_icon = pygame.transform.scale(attack_icon, (icon_size, icon_size))
shield_icon = pygame.image.load("./images/shield.svg")
shield_icon = pygame.transform.scale(shield_icon, (icon_size, icon_size))
heal_icon = pygame.image.load("./images/heal.svg")
heal_icon = pygame.transform.scale(heal_icon, (icon_size, icon_size))
energy_icon = pygame.image.load("./images/energy.svg")
energy_icon = pygame.transform.scale(energy_icon, (icon_size, icon_size))
dice_icon = pygame.image.load("./images/dice.svg")
dice_icon = pygame.transform.scale(dice_icon, (icon_size, icon_size))

class Card:
    def __init__(self, name, damage, bonus_damage, healing, shield, energy_cost, symbol, hue, rarity, targets_all=False):
        self.name = name
        self.damage = damage
        self.bonus_damage = bonus_damage
        self.healing = healing
        self.shield = shield
        self.energy_cost = energy_cost
        self.symbol = symbol
        self.hue = hue
        self.rarity = rarity
        self.targets_all = targets_all

def load_image(size, image_path: Path):
    try:
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (size, size))
    except pygame.error:
        print(f"Unable to load image: {image_path}")
        surface = pygame.Surface((size, size))
        surface.fill((255, 0, 0))  # Red rectangle as a placeholder
        return surface

class Character:
    def __init__(self, name, health, symbol):
        self.name = name
        self.health = health
        self.max_health = health
        self.shield = 0
        self.bonus_damage = 0
        self.energy = 3
        self.max_energy = 3
        self.symbol = symbol
        self.deck: List[Card]= []
        self.hand: List[Card] = []
        self.discard_pile :List[Card] = []
        self.hand_limit = 10
        self.size = 100
        self.image = load_image(size=self.size, image_path="./images/player.png")
        self.shake = 0

class Monster:
    def __init__(self, name, health, damage, symbol):
        self.name = name
        self.health = health
        self.max_health = health
        self.damage = damage
        self.symbol = symbol
        self.size = 100
        self.image = load_image(size=self.size, image_path=f"./images/{name.lower()}.png")
        self.shake = 0
        self.selected = False

class MonsterGroup:
    def __init__(self):
        self.monsters = []
        self.selected_index = 0

    def add_monster(self, monster):
        self.monsters.append(monster)
        if len(self.monsters) == 1:
            monster.selected = True

    def select_next(self):
        self.monsters[self.selected_index].selected = False
        self.selected_index = (self.selected_index + 1) % len(self.monsters)
        self.monsters[self.selected_index].selected = True

    def select_previous(self):
        self.monsters[self.selected_index].selected = False
        self.selected_index = (self.selected_index - 1) % len(self.monsters)
        self.monsters[self.selected_index].selected = True

    def get_selected_monster(self):
        return self.monsters[self.selected_index]

    def remove_dead_monsters(self):
        self.monsters = [monster for monster in self.monsters if monster.health > 0]
        if self.monsters:
            self.selected_index = min(self.selected_index, len(self.monsters) - 1)
            self.monsters[self.selected_index].selected = True

def render_player(player: Character):
    offset = random.randint(-player.shake, player.shake)
    screen.blit(player.image, (125 + offset, 250 + offset))
    if player.shake > 0:
        player.shake -= 1

def render_monsters(monster_group: MonsterGroup):
    num_monsters = len(monster_group.monsters)
    start_x = 575 - (num_monsters - 1) * 50
    for i, monster in enumerate(monster_group.monsters):
        offset = random.randint(-monster.shake, monster.shake)
        screen.blit(monster.image, (start_x + i * 100 + offset, 250 + offset))
        if monster.shake > 0:
            monster.shake -= 1
        if monster.selected:
            pygame.draw.rect(screen, YELLOW, (start_x + i * 100 - 5, 245, 110, 110), 3)

def render_text(text, x, y, color=BLACK, font=font):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def render_card(card, x, y, is_selected, hotkey=None):
    rgb = colorsys.hsv_to_rgb(card.hue, 0.3, 0.9)
    color = [int(255 * c) for c in rgb]
    if is_selected:
        color = YELLOW
    pygame.draw.rect(screen, color, (x, y, CARD_WIDTH, CARD_HEIGHT))
    pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
    
    render_text(card.name, x + 5, y + 5, font=card_font)
    screen.blit(attack_icon, (x + 5, y + 30))
    render_text(f"{card.damage}", x + 30, y + 30, font=card_font)
    screen.blit(dice_icon, (x + 5, y + 55))
    render_text(f"{card.bonus_damage}", x + 30, y + 55, font=card_font)
    screen.blit(heal_icon, (x + 5, y + 80))
    render_text(f"{card.healing}", x + 30, y + 80, font=card_font)
    screen.blit(shield_icon, (x + 5, y + 105))
    render_text(f"{card.shield}", x + 30, y + 105, font=card_font)
    screen.blit(energy_icon, (x + 5, y + 130))
    render_text(f"{card.energy_cost}", x + 30, y + 130, font=card_font)
    if card.targets_all:
        render_text("AOE", x + CARD_WIDTH - 35, y + CARD_HEIGHT - 20, font=small_font)
    if hotkey:
        render_text(str(hotkey), x + CARD_WIDTH - 20, y + 5, font=card_font)

def render_button(text, x, y, width, height):
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
    render_text(text, x + 10, y + 10)

def render_health_bar(x, y, width, height, current, maximum, color, name=None):
    pygame.draw.rect(screen, BLACK, (x - 1, y - 1, width + 2, height + 2))
    pygame.draw.rect(screen, color, (x, y, int(width * (current / maximum)), height))
    if name:
        render_text(name, x + 5, y + 2, color=WHITE, font=small_font)

def render_game_state(player, monster_group, dungeon_level, score, selected_card):
    screen.blit(background_image, (0, 0))
    
    # Render semi-transparent header bar
    header_height = 100
    s = pygame.Surface((SCREEN_WIDTH, header_height))
    s.set_alpha(128)
    s.fill(BEIGE)
    screen.blit(s, (0, 0))
    
    render_text(f"Dungeon Level: {dungeon_level}", 10, 10)
    render_text(f"Player Bonus: {player.bonus_damage}", 10, 40)
    
    # Render health and energy bars
    render_health_bar(200, 10, 200, 20, player.health, player.max_health, GREEN, "Player")
    render_text(f"{player.health}/{player.max_health}", 405, 10)
    render_health_bar(200, 40, 200, 20, player.energy, player.max_energy, BLUE, "Energy")
    render_text(f"{player.energy}/{player.max_energy}", 405, 40)
    
    # Render monster health bars
    for i, monster in enumerate(monster_group.monsters):
        y_offset = i * 30
        render_health_bar(500, 10 + y_offset, 200, 20, monster.health, monster.max_health, RED, monster.name)
        screen.blit(attack_icon, (710, 8 + y_offset))
        render_text(f"{monster.damage}", 735, 10 + y_offset, font=small_font)
    
    render_player(player)
    render_monsters(monster_group)
        
    # Draw bottom frame for cards with transparency
    s = pygame.Surface((SCREEN_WIDTH, CARD_HEIGHT + 40))
    s.set_alpha(128)
    s.fill((100, 100, 100))
    screen.blit(s, (0, SCREEN_HEIGHT - CARD_HEIGHT - 40))
    
    card_start_x = (SCREEN_WIDTH - (len(player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) // 2
    for i, card in enumerate(player.hand):
        render_card(card, card_start_x + i * (CARD_WIDTH + CARD_SPACING), SCREEN_HEIGHT - CARD_HEIGHT - 20, i == selected_card, hotkey=i+1)
    
    render_button("End Turn", SCREEN_WIDTH - 120, header_height + 10, 100, 40)
    render_button("Discard", SCREEN_WIDTH - 120, header_height + 60, 100, 40)
    
    # Render score in the bottom left corner
    render_text(f"Score: {score}", 10, SCREEN_HEIGHT - 30)
    
    pygame.display.flip()

def render_victory_state(score, new_cards, selected_card):
    screen.blit(background_image, (0, 0))
    
    render_text("Victory!", SCREEN_WIDTH // 2 - 50, 50)
    render_text(f"Score: {score}", SCREEN_WIDTH // 2 - 50, 100)
    render_text("Select a card to add to your deck:", SCREEN_WIDTH // 2 - 150, 150)
    
    for i, card in enumerate(new_cards):
        render_card(card, 50 + i * (CARD_WIDTH + CARD_SPACING), 200, i == selected_card, hotkey=i+1)
    
    render_text("Press number keys to select a card, or SPACE to skip", SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 50)
    pygame.display.flip()

def shuffle_deck(player: Character):
    player.deck.extend(player.discard_pile)
    player.discard_pile.clear()
    random.shuffle(player.deck)

def draw_card(player: Character):
    if not player.deck:
        shuffle_deck(player)
    if player.deck and len(player.hand) < player.hand_limit:
        player.hand.append(player.deck.pop())

def play_card(player: Character, monster_group: MonsterGroup, card_index:int):
    if 0 <= card_index < len(player.hand):
        card = player.hand[card_index]
        if player.energy >= card.energy_cost:
            player.bonus_damage += card.bonus_damage
            # HACK for not doing damage 0 damage cards
            if card.damage == 0:
                total_damage = 0
            else:
                total_damage = round(card.damage + player.bonus_damage)
            
            if card.targets_all:
                for monster in monster_group.monsters:
                    monster.health -= total_damage
                    monster.shake = 5
            else:
                selected_monster = monster_group.get_selected_monster()
                selected_monster.health -= total_damage
                selected_monster.shake = 5
            
            player.health = min(player.max_health, player.health + round(card.healing))
            player.shield += card.shield
            player.energy -= card.energy_cost
            
            if card.name == "Draw Card":
                draw_card(player)
            
            player.discard_pile.append(card)
            player.hand.pop(card_index)
        else:
            print("Not enough energy")

def generate_monster(level):
    names = ["Goblin", "Orc", "Troll", "Dragon", "Witch"]
    symbols = ['G', 'O', 'T', 'D', 'W']
    index = random.randint(0, len(names) - 1)
    
    # Vary monster stats based on their type
    base_health = 15 + level * 10 
    base_damage = 4 + level * 2   
    
    if names[index] == "Goblin":
        health = round(base_health * 0.8)
        damage = round(base_damage * 1.2)
    elif names[index] == "Orc":
        health = round(base_health * 1.2)
        damage = round(base_damage * 0.8)
    elif names[index] == "Troll":
        health = round(base_health * 1.5)
        damage = round(base_damage)
    elif names[index] == "Dragon":
        health = round(base_health * 2)
        damage = round(base_damage * 1.5)
    else:  # Witch
        health = round(base_health)
        damage = round(base_damage * 1.3)
    
    return Monster(names[index], health, damage, symbols[index])

def generate_monster_group(level):
    monster_group = MonsterGroup()
    num_monsters = min(1 + level // 2, 3)  # Start with 1 monster, add 1 every 2 levels, max 3
    for _ in range(num_monsters):
        monster_group.add_monster(generate_monster(level))
    return monster_group

def generate_card_pool():
    return [
        Card("Fireball", 12, 0, 0, 0, 2, 'F', random.random(), 0.7),
        Card("Ice Shield", 0, 0, 0, 12, 2, 'I', random.random(), 0.7),
        Card("Lightning Strike", 10, 2, 0, 0, 2, 'L', random.random(), 0.7),
        Card("Healing Potion", 0, 0, 15, 0, 2, 'H', random.random(), 0.7),
        Card("Defensive Stance", 5, 0, 0, 10, 2, 'D', random.random(), 0.7),
        Card("Vampiric Touch", 8, 0, 8, 0, 2, 'V', random.random(), 0.6),
        Card("Rage", 0, 5, 0, 0, 1, 'R', random.random(), 0.8),
        Card("Mana Surge", 0, 0, 0, 0, 0, 'M', random.random(), 0.5),
        Card("Poison Dagger", 6, 2, 0, 0, 1, 'P', random.random(), 0.7),
        Card("Holy Light", 0, 0, 10, 5, 2, 'H', random.random(), 0.6),
        Card("Time Warp", 0, 0, 0, 0, 3, 'T', random.random(), 0.4),
        Card("Earthquake", 15, 0, 0, 0, 3, 'E', random.random(), 0.5, targets_all=True),
        Card("Charm", 0, 0, 0, 15, 2, 'C', random.random(), 0.6),
        Card("Whirlwind", 8, 0, 0, 8, 2, 'W', random.random(), 0.7, targets_all=True),
        Card("Dragon's Breath", 20, 0, 0, 0, 4, 'D', random.random(), 0.3, targets_all=True)
    ]

def victory_screen(player, score):
    card_pool = generate_card_pool()
    new_cards = random.choices(card_pool, weights=[card.rarity for card in card_pool], k=3)
    
    selected_card = 0
    running = True
    
    while running:
        render_victory_state(score, new_cards, selected_card)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    selected_card = event.key - pygame.K_1
                    return new_cards[selected_card]
                elif event.key == pygame.K_SPACE:
                    return None
        
        pygame.time.wait(100)

def game_loop():
    player = Character("Hero", 100, '@')
    player.deck = [
        Card("Quick Strike", 8, 0, 0, 0, 1, 'Q', random.random(), 1),
        Card("Boon", 0, 4, 0, 0, 0, 'B', random.random(), 1),
        Card("Heal", 0, 0, 8, 0, 1, 'H', random.random(), 1),
        Card("Shield", 0, 0, 0, 8, 1, 'S', random.random(), 1),
        Card("Power Strike", 15, 0, 0, 0, 2, 'P', random.random(), 1),
        Card("Major Heal", 0, 0, 15, 0, 2, 'M', random.random(), 1),
        Card("Draw Card", 0, 0, 0, 0, 1, 'C', random.random(), 1),
        Card("Cleave", 6, 0, 0, 0, 2, 'V', random.random(), 1, targets_all=True)
    ] * 2
    random.shuffle(player.deck)
    
    dungeon_level = 1
    score = 0
    stages_cleared = 0
    selected_card = -1
    player_turn = True
    
    monster_group = generate_monster_group(dungeon_level)
    
    for _ in range(5):
        draw_card(player)
    
    running = True
    clock = pygame.time.Clock()

    while running and player.health > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                card_start_x = (SCREEN_WIDTH - (len(player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) // 2
                for i in range(len(player.hand)):
                    card_rect = pygame.Rect(card_start_x + i * (CARD_WIDTH + CARD_SPACING), SCREEN_HEIGHT - CARD_HEIGHT - 20, CARD_WIDTH, CARD_HEIGHT)
                    if card_rect.collidepoint(mouse_x, mouse_y):
                        selected_card = i
                        break

                end_turn_rect = pygame.Rect(SCREEN_WIDTH - 120, 110, 100, 40)
                if end_turn_rect.collidepoint(mouse_x, mouse_y):
                    player_turn = False
                
                discard_rect = pygame.Rect(SCREEN_WIDTH - 120, 160, 100, 40)
                if discard_rect.collidepoint(mouse_x, mouse_y) and selected_card != -1:
                    player.discard_pile.append(player.hand.pop(selected_card))
                    selected_card = -1

            elif event.type == pygame.KEYDOWN:
                num_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
                for i, key in enumerate(num_keys):
                    if event.key == key and i < len(player.hand):
                        selected_card = i
                        play_card(player, monster_group, selected_card)
                        selected_card = -1
                        break

                if event.key == pygame.K_e:
                    player_turn = False
                elif event.key == pygame.K_UP:
                    monster_group.select_previous()
                elif event.key == pygame.K_DOWN:
                    monster_group.select_next()
        # NOTE 
        if not player_turn:
            for monster in monster_group.monsters:
                damage = round(max(0, monster.damage - player.shield))
                player.health -= damage
                player.shake = 5  # Start shaking the player
            player.shield = 0
            player.energy = player.max_energy
            player.bonus_damage = 0
            player_turn = True
            
            player.discard_pile.extend(player.hand)
            player.hand.clear()
            for _ in range(5):
                draw_card(player)
        
        monster_group.remove_dead_monsters()
        
        if not monster_group.monsters:
            score += sum(monster.max_health + monster.damage for monster in monster_group.monsters)
            dungeon_level += 1
            stages_cleared += 1
            player.health = min(player.max_health, player.health + dungeon_level * 5)
            player.energy = player.max_energy

            if stages_cleared % 2 == 0 and player.max_energy < 10:
                player.max_energy += 1

            new_card = victory_screen(player, score)
            if new_card:
                player.deck.append(new_card)
            
            monster_group = generate_monster_group(dungeon_level)
        
        render_game_state(player, monster_group, dungeon_level, score, selected_card)
        clock.tick(60)
    
    # Game over screen
    screen.fill(WHITE)
    render_text("GAME OVER", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 20)
    render_text(f"Final Score: {score}", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 20)
    pygame.display.flip()
    
    pygame.time.wait(3000)

def main():
    game_loop()
    pygame.quit()

if __name__ == "__main__":
    main()