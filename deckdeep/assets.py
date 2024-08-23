import pygame
from typing import Tuple
from deckdeep.config import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, ICON_SIZE, PLAYER_SIZE, scale

class GameAssets:
    def __init__(self):
        # background
        self.background_image: pygame.Surface = self.load_and_scale("./assets/images/backgrounds/background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_screen_image: pygame.Surface = self.load_and_scale("./assets/images/backgrounds/deckdeep.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_over_image: pygame.Surface = self.load_and_scale("./assets/images/backgrounds/youlost.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

        # ui elements
        self.parchment_texture: pygame.Surface = self.load_and_scale("./assets/images/ui_elements/parchment_texture.png", (CARD_WIDTH, CARD_HEIGHT))

        # icons
        self.attack_icon: pygame.Surface = self.load_and_scale("./assets/images/icons/attack.svg", (ICON_SIZE, ICON_SIZE))
        self.shield_icon: pygame.Surface = self.load_and_scale("./assets/images/icons/shield.svg", (ICON_SIZE, ICON_SIZE))
        self.heal_icon: pygame.Surface = self.load_and_scale("./assets/images/icons/heal.svg", (ICON_SIZE, ICON_SIZE))
        self.energy_icon: pygame.Surface = self.load_and_scale("./assets/images/icons/energy.svg", (ICON_SIZE, ICON_SIZE))
        self.dice_icon: pygame.Surface = self.load_and_scale("./assets/images/icons/dice.svg", (ICON_SIZE, ICON_SIZE))
        self.draw_icon: pygame.Surface = self.load_and_scale("./assets/images/icons/draw.svg", (ICON_SIZE, ICON_SIZE))
        self.health_cost: pygame.Surface = self.load_and_scale("./assets/images/icons/health_cost.svg", (ICON_SIZE, ICON_SIZE))

        # Units
        self.player: pygame.Surface = self.load_and_scale("./assets/images/characters/player.png", (PLAYER_SIZE, PLAYER_SIZE))

        # Misc
        self.music_path: str = './assets/music/'

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
