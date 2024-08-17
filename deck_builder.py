import pygame
from pathlib import Path
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("D&D Deckbuilder")

# Load font
font = pygame.font.Font(None, 24)

class Card:
    def __init__(self, name, damage, bonus_damage, healing, shield, energy_cost, symbol):
        self.name = name
        self.damage = damage
        self.bonus_damage = bonus_damage
        self.healing = healing
        self.shield = shield
        self.energy_cost = energy_cost
        self.symbol = symbol

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
        self.deck = []
        self.hand = []
        self.discard_pile = []
        self.hand_limit = 10
        self.size = 100
        self.image = load_image(size=self.size, image_path="./images/player.png")

class Monster:
    def __init__(self, name, health, damage, symbol):
        self.name = name
        self.health = health
        self.max_health = health
        self.damage = damage
        self.symbol = symbol
        self.size = 100
        self.image = load_image(size=self.size, image_path=f"./images/{name.lower()}.png")

def render_player(player: Character):
    screen.blit(player.image, (125, 300))

def render_monster(monster: Monster):
    screen.blit(monster.image, (575, 300))

def render_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def render_card(card, x, y, is_selected, hotkey=None):
    color = YELLOW if is_selected else GRAY
    pygame.draw.rect(screen, color, (x, y, CARD_WIDTH, CARD_HEIGHT))
    pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
    
    render_text(card.name, x + 5, y + 5)
    render_text(f"D: {card.damage}", x + 5, y + 30)
    render_text(f"B: {card.bonus_damage}", x + 5, y + 55)
    render_text(f"H: {card.healing}", x + 5, y + 80)
    render_text(f"S: {card.shield}", x + 5, y + 105)
    render_text(f"E: {card.energy_cost}", x + 5, y + 130)
    if hotkey:
        render_text(str(hotkey), x + 50, y + 130)

def render_button(text, x, y, width, height):
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
    render_text(text, x + 10, y + 10)

def render_game_state(player, monster, dungeon_level, score, selected_card):
    screen.fill(WHITE)
    
    render_text(f"Dungeon Level: {dungeon_level}", 10, 10)
    render_text(f"Score: {score}", 10, 40)
    
    render_text(f"Player Health: {player.health}/{player.max_health}", 10, 70)
    render_text(f"Player Bonus: {player.bonus_damage}", 10, 100)
    render_text(f"Player Energy: {player.energy}/{player.max_energy}", 10, 130)
    render_text(f"Player Shield: {player.shield}", 10, 160)
    
    render_text(f"{monster.name} Health: {monster.health}/{monster.max_health}", 400, 70)
    render_text(f"{monster.name} Damage: {monster.damage}", 400, 100)
    
    render_player(player)
    render_monster(monster)
        
    card_start_x = (SCREEN_WIDTH - (len(player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) // 2
    for i, card in enumerate(player.hand):
        render_card(card, card_start_x + i * (CARD_WIDTH + CARD_SPACING), SCREEN_HEIGHT - CARD_HEIGHT - 20, i == selected_card, hotkey=i)
    
    render_button("End Turn", SCREEN_WIDTH - 120, 10, 100, 40)
    render_button("Discard", SCREEN_WIDTH - 120, 60, 100, 40)
    
    pygame.display.flip()

def render_victory_state(score, new_cards):
    screen.fill(WHITE)
    render_text("Victory!", SCREEN_WIDTH // 2 - 50, 50)
    render_text(f"Score: {score}", SCREEN_WIDTH // 2 - 50, 100)
    render_text("Select a card to add to your deck:", SCREEN_WIDTH // 2 - 150, 150)
    
    for i, card in enumerate(new_cards):
        render_card(card, 50 + i * (CARD_WIDTH + CARD_SPACING), 200, False)
    
    render_text("Press LEFT/RIGHT to navigate, ENTER to select, or SPACE to skip", SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 50)
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

def play_card(player, monster, card_index):
    if 0 <= card_index < len(player.hand):
        card = player.hand[card_index]
        if player.energy >= card.energy_cost:
            player.bonus_damage += card.bonus_damage
            monster.health -= card.damage + player.bonus_damage
            player.health = min(player.max_health, player.health + card.healing)
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
    base_health = 20 + level * 10
    base_damage = 5 + level * 2
    
    if names[index] == "Goblin":
        health = int(base_health * 0.8)
        damage = int(base_damage * 1.2)
    elif names[index] == "Orc":
        health = int(base_health * 1.2)
        damage = int(base_damage * 0.8)
    elif names[index] == "Troll":
        health = int(base_health * 1.5)
        damage = base_damage
    elif names[index] == "Dragon":
        health = int(base_health * 2)
        damage = int(base_damage * 1.5)
    else:  # Witch
        health = base_health
        damage = int(base_damage * 1.3)
    
    return Monster(names[index], health, damage, symbols[index])

def victory_screen(player, score):
    new_cards = [
        Card("Fireball", 12, 0, 0, 0, 2, 'F'),
        Card("Ice Shield", 0, 0, 0, 12, 2, 'I'),
        Card("Lightning Strike", 10, 2, 0, 0, 2, 'L')
    ]
    
    selected_card = 0
    running = True
    
    while running:
        render_victory_state(score, new_cards)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_card = (selected_card - 1) % len(new_cards)
                elif event.key == pygame.K_RIGHT:
                    selected_card = (selected_card + 1) % len(new_cards)
                elif event.key == pygame.K_RETURN:
                    return new_cards[selected_card]
                elif event.key == pygame.K_SPACE:
                    return None
        
        pygame.time.wait(100)

def game_loop():
    player = Character("Hero", 100, '@')
    player.deck = [
        Card("Quick Strike", 8, 0, 0, 0, 1, 'Q'),
        Card("Boon", 0, 4, 0, 0, 0, 'B'),
        Card("Heal", 0, 0, 8, 0, 1, 'H'),
        Card("Shield", 0, 0, 0, 8, 1, 'S'),
        Card("Power Strike", 15, 0, 0, 0, 2, 'P'),
        Card("Major Heal", 0, 0, 15, 0, 2, 'M'),
        Card("Draw Card", 0, 0, 0, 0, 1, 'C')
    ] * 2
    random.shuffle(player.deck)
    
    dungeon_level = 1
    score = 0
    stages_cleared = 0
    selected_card = -1
    player_turn = True
    
    monster = generate_monster(dungeon_level)
    
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

                end_turn_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 100, 40)
                if end_turn_rect.collidepoint(mouse_x, mouse_y):
                    player_turn = False
                
                discard_rect = pygame.Rect(SCREEN_WIDTH - 120, 60, 100, 40)
                if discard_rect.collidepoint(mouse_x, mouse_y) and selected_card != -1:
                    player.discard_pile.append(player.hand.pop(selected_card))
                    selected_card = -1

            elif event.type == pygame.KEYDOWN:
                num_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
                for i in range(len(player.hand)):
                    if event.key == num_keys[i]:
                        selected_card = i
                        break

                if event.key == pygame.K_e:
                    player_turn = False

                if selected_card != -1:
                    play_card(player, monster, selected_card)
                    selected_card = -1

        if not player_turn:
            damage = max(0, monster.damage - player.shield)
            player.health -= damage
            player.shield = 0
            player.energy = player.max_energy
            player_turn = True
            
            player.discard_pile.extend(player.hand)
            player.hand.clear()
            for _ in range(5):
                draw_card(player)
        
        if monster.health <= 0:
            score += monster.max_health + monster.damage
            dungeon_level += 1
            stages_cleared += 1
            player.health = min(player.max_health, player.health + dungeon_level * 5)
            
            if stages_cleared % 2 == 0 and player.max_energy < 10:
                player.max_energy += 1

            new_card = victory_screen(player, score)
            if new_card:
                player.deck.append(new_card)
            
            monster = generate_monster(dungeon_level)
        
        render_game_state(player, monster, dungeon_level, score, selected_card)
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