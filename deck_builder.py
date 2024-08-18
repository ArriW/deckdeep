import pygame
from pathlib import Path
import random
import colorsys
from typing import List, Tuple

# Initialize Pygame
pygame.init()


# Constants
SCREEN_WIDTH    = 1450 
SCREEN_HEIGHT   = SCREEN_WIDTH * 2/3 

CALIBRATED_WIDTH = 1200
def scale(original_pixel_weight:int) -> int:
    return round(original_pixel_weight/CALIBRATED_WIDTH*SCREEN_WIDTH) 

CARD_WIDTH      = scale(160)
CARD_HEIGHT     = scale(240)
CARD_SPACING    = scale(10)
ICON_SIZE       = scale(36)
PLAYER_SIZE     = scale(100) 

# Colors
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
GRAY    = (200, 200, 200)
YELLOW  = (255, 255, 0)
GREEN   = (0, 255, 0)
BLUE    = (0, 0, 255)
RED     = (255, 0, 0)
BEIGE   = (245, 245, 220)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("D&D Deckbuilder")

# Load fonts
font          = pygame.font.Font(None, scale(26))
small_font    = pygame.font.Font(None, scale(23))
card_font     = pygame.font.Font(None, scale(30))

class GameAssets:
    def __init__(self):
        # background
        self.background_image   : pygame.Surface = self.load_and_scale("./assets/images/backgrounds/background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_screen_image : pygame.Surface = self.load_and_scale("./assets/images/backgrounds/deckdeep.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_over_image    : pygame.Surface = self.load_and_scale("./assets/images/backgrounds/youlost.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

        # ui elements
        self.parchment_texture : pygame.Surface = self.load_and_scale("./assets/images/ui_elements/parchment_texture.png", (CARD_WIDTH, CARD_HEIGHT))

        # icons
        self.attack_icon : pygame.Surface = self.load_and_scale("./assets/images/icons/attack.svg", (ICON_SIZE, ICON_SIZE))
        self.shield_icon : pygame.Surface = self.load_and_scale("./assets/images/icons/shield.svg", (ICON_SIZE, ICON_SIZE))
        self.heal_icon   : pygame.Surface = self.load_and_scale("./assets/images/icons/heal.svg", (ICON_SIZE, ICON_SIZE))
        self.energy_icon : pygame.Surface = self.load_and_scale("./assets/images/icons/energy.svg", (ICON_SIZE, ICON_SIZE))
        self.dice_icon   : pygame.Surface = self.load_and_scale("./assets/images/icons/dice.svg", (ICON_SIZE, ICON_SIZE))

        # Units
        self.player      : pygame.Surface = self.load_and_scale("./assets/images/characters/player.png", (PLAYER_SIZE,PLAYER_SIZE))

    @staticmethod
    def load_and_scale(path: str, size: Tuple[int, int]) -> pygame.Surface:
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, size)
        except pygame.error:
            print(f"Unable to load image: {path}")
            surface = pygame.Surface(size)
            surface.fill((255, 0, 0))  # Red rectangle as a placeholder
            return surface

# Instantiate the assets
assets = GameAssets()

class Card:
    def __init__(self, name, damage, bonus_damage, healing, shield, energy_cost, symbol, hue, rarity, targets_all=False):
        self.name           = name
        self.damage         = damage
        self.bonus_damage   = bonus_damage
        self.healing        = healing
        self.shield         = shield
        self.energy_cost    = energy_cost
        self.symbol         = symbol
        self.hue            = hue
        self.rarity         = rarity
        self.targets_all    = targets_all

class Character:
    def __init__(self, name, health, symbol):
        self.name         = name
        self.health       = health
        self.max_health   = health
        self.shield       = 0
        self.bonus_damage = 0
        self.energy       = 3
        self.max_energy   = 3
        self.symbol       = symbol
        self.hand_limit   = 10
        self.deck         : List[Card]= []
        self.hand         : List[Card] = []
        self.discard_pile : List[Card] = []
        self.size         = PLAYER_SIZE
        self.image        = assets.player 
        self.shake        = 0
        self.health_gain_on_skip :int  = 5

class MonsterType:
    def __init__(self, name, symbol, health_mult, damage_mult, rarity):
        self.name           = name
        self.symbol         = symbol
        self.health_mult    = health_mult
        self.damage_mult    = damage_mult
        self.rarity         = rarity
        self.power          = health_mult * damage_mult

class Monster:
    def __init__(self, monster_type: MonsterType, level: int):
        self.name         = monster_type.name
        self.symbol       = monster_type.symbol
        base_health       = round(15 + level * 10)
        base_damage       = round(4 + level * 1.3)
        self.health       = round(base_health * monster_type.health_mult)
        self.max_health   = self.health
        self.damage       = round(base_damage * monster_type.damage_mult)
        self.size         = scale(100)
        self.image        = assets.load_and_scale(path=f"./assets/images/characters/{self.name.lower()}.png",size=(self.size,self.size))
        self.shake        = 0
        self.selected     = False

class MonsterGroup:
    def __init__(self):
        self.monsters         = []
        self.selected_index   = 0

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
    screen.blit(player.image, (
        scale(120) + offset, 
        scale(250) + offset
    ))
    if player.shake > 0:
        player.shake -= 1

def render_monsters(monster_group: MonsterGroup):
    num_monsters = len(monster_group.monsters)
    start_x = scale(575) - (num_monsters - 1) * scale(50)
    for i, monster in enumerate(monster_group.monsters):
        offset = random.randint(-monster.shake, monster.shake)
        screen.blit(monster.image, (
            start_x + i * scale(100) + offset, 
            scale(250) + offset
        ))
        if monster.shake > 0:
            monster.shake -= 1
        if monster.selected:
            pygame.draw.rect(screen, YELLOW, (
                start_x + i * scale(100) - scale(5), 
                scale(245), 
                scale(110), 
                scale(110)
            ), 3)

def render_text(text, x, y, color=BLACK, font=font):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def render_card(card, x, y, is_selected, hotkey=None):
    x_offset = ICON_SIZE + scale(16)
    x_anchor = scale(10)
    y_offset = ICON_SIZE
    y_text_offset = scale(5)

    # Draw the card background
    screen.blit(assets.parchment_texture, (x, y))

    # Draw the selection border
    border_color = YELLOW if is_selected else BLACK
    pygame.draw.rect(screen, border_color, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
    
    # Render the card name centered at the top
    name_surface = card_font.render(card.name, True, BLACK)
    name_x = x + (CARD_WIDTH - name_surface.get_width()) // 2
    screen.blit(name_surface, (name_x, y + scale(10)))

    # Vertical offset for placing the stats
    current_y = y + y_offset + scale(15)

    # Render each stat only if iti is greater than 0, moving the next stat up
    if card.damage > 0:
        attack_text = f"{card.damage}"
        if card.targets_all:
            attack_text += " (AOE)"
        screen.blit(assets.attack_icon, (x + x_anchor, current_y))
        render_text(attack_text, x + x_offset, current_y + y_text_offset, font=card_font)
        current_y += y_offset 

    if card.bonus_damage > 0:
        screen.blit(assets.dice_icon, (x + x_anchor, current_y))
        render_text(f"{card.bonus_damage}", x + x_offset, current_y + y_text_offset, font=card_font)
        current_y += y_offset 

    if card.healing > 0:
        screen.blit(assets.heal_icon, (x + x_anchor, current_y))
        render_text(f"{card.healing}", x + x_offset, current_y + y_text_offset, font=card_font)
        current_y += y_offset 

    if card.shield > 0:
        screen.blit(assets.shield_icon, (x + x_anchor, current_y))
        render_text(f"{card.shield}", x + x_offset, current_y + y_text_offset, font=card_font)
        current_y += y_offset 

    # Always render the energy cost in the bottom right corner
    energy_x = x + CARD_WIDTH - x_offset + ICON_SIZE
    energy_y = y + CARD_HEIGHT - ICON_SIZE 
    screen.blit(assets.energy_icon, (energy_x - x_offset, energy_y))
    render_text(f"{card.energy_cost}", energy_x, energy_y + y_text_offset, font=card_font)

    # Render the hotkey in the bottom left corner if provided
    if hotkey:
        render_text(str(hotkey), x + x_anchor, y + CARD_HEIGHT - x_offset, font=card_font)


def render_button(text, x, y, width, height):
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
    render_text(text, x + scale(10), y + scale(10))


def render_health_bar(x, y, width, height, current, maximum, color, name=None):
    pygame.draw.rect(screen, BLACK, (
        x - scale(1), 
        y - scale(1), 
        width + scale(2), 
        height + scale(2)
    ))
    pygame.draw.rect(screen, color, (
        x, 
        y, 
        int(width * (current / maximum)), 
        height
    ))
    if name:
        render_text(name, x + scale(5), y + scale(2), color=WHITE, font=small_font)


def render_game_state(player, monster_group, dungeon_level, score, selected_card):
    screen.blit(assets.background_image, (0, 0))
    
    # Render semi-transparent header bar
    header_height = scale(100)
    s = pygame.Surface((SCREEN_WIDTH, header_height))
    s.set_alpha(128)
    s.fill(BEIGE)
    screen.blit(s, (0, 0))
    
    render_text(f"Dungeon Level: {dungeon_level}", scale(10), scale(10))
    render_text(f"Score: {score}", scale(10), scale(40))
    render_text(f"Player Bonus: {player.bonus_damage}", scale(10), scale(70))
    
    # Render health and energy bars
    render_health_bar(scale(200), scale(10), scale(200), scale(20), player.health, player.max_health, GREEN, "Player")
    render_text(f"{player.health}/{player.max_health}", scale(405), scale(10))
    
    # Render player shield as a transparent overlay on the health bar
    if player.shield > 0:
        shield_width = int(scale(200) * (player.shield / player.max_health))
        s = pygame.Surface((shield_width, scale(20)))
        s.set_alpha(128)
        s.fill(BLUE)
        screen.blit(s, (scale(400) - shield_width, scale(10)))
        render_text(f"+{player.shield}", scale(405) - shield_width, scale(10), color=WHITE, font=small_font)
    
    render_health_bar(scale(200), scale(40), scale(200), scale(20), player.energy, player.max_energy, BLUE, "Energy")
    render_text(f"{player.energy}/{player.max_energy}", scale(405), scale(40))
    
    # Render monster health bars
    for i, monster in enumerate(monster_group.monsters):
        y_offset = i * scale(30)
        render_health_bar(scale(500), scale(10) + y_offset, scale(200), scale(20), monster.health, monster.max_health, RED, monster.name)
        screen.blit(assets.attack_icon, (scale(710), scale(8) + y_offset))
        render_text(f"{monster.damage}", scale(735), scale(10) + y_offset, font=small_font)
    
    render_player(player)
    render_monsters(monster_group)
        
    # Draw bottom frame for cards with transparency
    s = pygame.Surface((SCREEN_WIDTH, CARD_HEIGHT + scale(40)))
    s.set_alpha(128)
    s.fill((100, 100, 100))
    screen.blit(s, (0, SCREEN_HEIGHT - CARD_HEIGHT - scale(40)))
    
    card_start_x = (SCREEN_WIDTH - (len(player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) // 2
    for i, card in enumerate(player.hand):
        render_card(card, card_start_x + i * (CARD_WIDTH + CARD_SPACING), SCREEN_HEIGHT - CARD_HEIGHT - scale(20), i == selected_card, hotkey=i+1)
    
    render_button("End Turn", SCREEN_WIDTH - scale(120), header_height + scale(10), scale(100), scale(40))
    render_button("Discard", SCREEN_WIDTH - scale(120), header_height + scale(60), scale(100), scale(40))
    
    pygame.display.flip()


def render_victory_state(score, new_cards, selected_card):
    screen.blit(assets.background_image, (0, 0))
    header_height = scale(200)
    s = pygame.Surface((SCREEN_WIDTH, header_height))
    s.set_alpha(128)
    s.fill(BEIGE)
    screen.blit(s, (0, 0))
    
    render_text("Victory!", SCREEN_WIDTH // 2 - 50, 50)
    render_text(f"Score: {score}", SCREEN_WIDTH // 2 - 50, 100)
    render_text("Select a card to add to your deck:", SCREEN_WIDTH // 2 - 150, 150)
    render_text("Press number keys to select a card, or SPACE to skip", SCREEN_WIDTH // 2 - 250, 150+25)
    
    for i, card in enumerate(new_cards):
        render_card(card, scale(250) + i * (CARD_WIDTH + CARD_SPACING), scale(250), i == selected_card, hotkey=i+1)
    
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

def play_card(player: Character, monster_group: MonsterGroup, card_index: int, score: int):
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
                    old_health = monster.health
                    monster.health = max(0, monster.health - total_damage)
                    score += old_health - monster.health
                    if total_damage > 0:
                        monster.shake = 5
            else:
                selected_monster = monster_group.get_selected_monster()
                old_health = selected_monster.health
                selected_monster.health = max(0, selected_monster.health - total_damage)
                score += old_health - selected_monster.health
                if total_damage > 0:
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
    return score

# Define monster types
monster_types = [
    MonsterType("Goblin", 'G', 0.8, 1.0, 1.0),
    MonsterType("Zombie_1", 'Z1', 0.3, 1.4, 1.0),
    MonsterType("Zombie_2", 'Z2', 1.2, 0.5, 1.0),
    MonsterType("Orc", 'O', 1.0, 1.0, 0.8),
    MonsterType("Troll", 'T', 1.2, 1.1, 0.6),
    MonsterType("Dragon", 'D', 1.5, 1.3, 0.3),
    MonsterType("Witch", 'W', 0.9, 1.2, 0.5)
]

def generate_monster(level):
    weights = [1 / (mt.power ** 2) for mt in monster_types]  # Inverse square of power for weights
    monster_type = random.choices(monster_types, weights=weights)[0]
    return Monster(monster_type, level)

def generate_monster_group(level):
    monster_group = MonsterGroup()
    num_monsters = min(1 + level // 2, 3)  # Start with 1 monster, add 1 every 2 levels, max 3
    monsters_to_fight = random.randint(1,num_monsters)
    for _ in range(monsters_to_fight):
        monster_group.add_monster(generate_monster(level))
    return monster_group

def generate_card_pool():
    return [
        Card("Draw Card", 0, 0, 0, 0, 1, 'C', random.random(), 1),
        Card("Boon", 0, 4, 0, 0, 0, 'B', random.random(), 1),
        Card("Cleave", 6, 0, 0, 0, 2, 'V', random.random(), 1, targets_all=True),
        Card("Major Heal", 0, 0, 15, 0, 2, 'M', random.random(), 1),
        Card("Fireball", 12, 0, 0, 0, 2, 'F', random.random(), 0.7, targets_all=True),
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

def victory_screen(player: Character, score: int ):
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
                    player.max_health += player.health_gain_on_skip
                    return None
        
        pygame.time.wait(100)

def start_screen():
    screen.blit(assets.start_screen_image, (0, 0))
    render_text("Press any key to start", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                waiting = False
    return True

def game_over_screen(score):
    screen.blit(assets.game_over_image, (0, 0))
    render_text(f"Final Score: {score}", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 100)
    render_text("Press any key to continue", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                waiting = False
    return True

def game_loop():
    player = Character("Hero", 100, '@')
    player.deck = [
        Card("Quick Strike", 8, 0, 0, 0, 1, 'Q', random.random(), 1),
        Card("Quick Strike", 8, 0, 0, 0, 1, 'Q', random.random(), 1),
        Card("Quick Strike", 8, 0, 0, 0, 1, 'Q', random.random(), 1),
        Card("Quick Strike", 8, 0, 0, 0, 1, 'Q', random.random(), 1),
        Card("Boon", 0, 4, 0, 0, 0, 'B', random.random(), 1),
        Card("Boon", 0, 4, 0, 0, 0, 'B', random.random(), 1),
        Card("Shield", 0, 0, 0, 8, 1, 'S', random.random(), 1),
        Card("Shield", 0, 0, 0, 8, 1, 'S', random.random(), 1),
        Card("Shield", 0, 0, 0, 8, 1, 'S', random.random(), 1),
        Card("Heal", 0, 0, 8, 0, 1, 'H', random.random(), 1),
        Card("Power Strike", 15, 0, 0, 0, 2, 'P', random.random(), 1),
        Card("Draw Card", 0, 0, 0, 0, 1, 'C', random.random(), 1),
        Card("Draw Card", 0, 0, 0, 0, 1, 'C', random.random(), 1),
        Card("Cleave", 6, 0, 0, 0, 2, 'V', random.random(), 1, targets_all=True)
    ] 
    random.shuffle(player.deck)
    
    dungeon_level = 1
    score = 0
    stages_cleared = 0
    selected_card = -1
    player_turn = True
    
    monster_group = generate_monster_group(dungeon_level)
    
    for _ in range(6):
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

                end_turn_rect = pygame.Rect(SCREEN_WIDTH - scale(120), scale(110), scale(100), scale(40))
                if end_turn_rect.collidepoint(mouse_x, mouse_y):
                    player_turn = False
                
                discard_rect = pygame.Rect(SCREEN_WIDTH - scale(120), scale(160), scale(100), scale(40))
                if discard_rect.collidepoint(mouse_x, mouse_y) and selected_card != -1:
                    player.discard_pile.append(player.hand.pop(selected_card))
                    selected_card = -1

            elif event.type == pygame.KEYDOWN:
                num_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
                for i, key in enumerate(num_keys):
                    if event.key == key and i < len(player.hand):
                        selected_card = i
                        score = play_card(player, monster_group, selected_card, score)
                        selected_card = -1
                        break

                if event.key == pygame.K_e:
                    player_turn = False
                elif event.key == pygame.K_UP:
                    monster_group.select_previous()
                elif event.key == pygame.K_DOWN:
                    monster_group.select_next()
        
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
            
            # Reset player's hand for the new fight
            player.discard_pile.extend(player.hand)
            player.hand.clear()
            for _ in range(5):
                draw_card(player)
        
        render_game_state(player, monster_group, dungeon_level, score, selected_card)
        clock.tick(60)
    
    return score

def main():
    running = True
    while running:
        if start_screen():
            final_score = game_loop()
            if not game_over_screen(final_score):
                running = False
        else:
            running = False
    
    pygame.quit()

if __name__ == "__main__":
    main()