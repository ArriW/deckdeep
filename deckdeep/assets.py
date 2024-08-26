import pygame
from typing import Tuple
from deckdeep.config import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, ICON_SIZE, PLAYER_SIZE, scale

class GameAssets:
    def __init__(self):
        # background
        self.background_image: pygame.Surface = self.load_and_scale_background("./assets/images/backgrounds/background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.victory_image: pygame.Surface = self.load_and_scale_background("./assets/images/backgrounds/victory.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_screen_image: pygame.Surface = self.load_and_scale_background("./assets/images/backgrounds/deckdeep.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_over_image: pygame.Surface = self.load_and_scale_background("./assets/images/backgrounds/youlost.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

        # ui elements
        self.parchment_texture: pygame.Surface = self.load_and_scale_ui("./assets/images/ui_elements/parchment_texture.png", (CARD_WIDTH, CARD_HEIGHT))

        # icons
        self.attack_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/attack.png", (ICON_SIZE, ICON_SIZE))
        self.shield_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/shield.png", (ICON_SIZE, ICON_SIZE))
        self.heal_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/heal.png", (ICON_SIZE, ICON_SIZE))
        self.energy_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/energy.png", (ICON_SIZE, ICON_SIZE))
        self.dice_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/dice.png", (ICON_SIZE, ICON_SIZE))
        self.draw_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/draw.png", (ICON_SIZE, ICON_SIZE))
        self.health_cost: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/health_cost.png", (ICON_SIZE, ICON_SIZE))
        
        # New status effect icons
        self.bleed_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/bleed.png", (ICON_SIZE, ICON_SIZE))
        self.energy_bonus_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/energy_bonus.png", (ICON_SIZE, ICON_SIZE))
        self.health_regain_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/health_regain.png", (ICON_SIZE, ICON_SIZE))
        self.strength_icon: pygame.Surface = self.load_and_scale_ui("./assets/images/icons/strength.png", (ICON_SIZE, ICON_SIZE))
        
        # Units
        self.player: pygame.Surface = self.load_and_scale_ui("./assets/images/characters/player.png", (PLAYER_SIZE, PLAYER_SIZE))

        # Misc
        self.music_path: str = './assets/music/'

    @staticmethod
    def load_and_scale_background(path: str, size: Tuple[int, int]) -> pygame.Surface:
        try:
            image = pygame.image.load(path)
            image_ratio = image.get_width() / image.get_height()
            screen_ratio = size[0] / size[1]

            if image_ratio > screen_ratio:
                # Image is wider, scale to fit height
                new_height = size[1]
                new_width = int(new_height * image_ratio)
            else:
                # Image is taller or same ratio, scale to fit width
                new_width = size[0]
                new_height = int(new_width / image_ratio)

            scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))

            # Create a surface of the desired size and blit the scaled image onto it
            final_surface = pygame.Surface(size)
            x_offset = (size[0] - new_width) // 2
            y_offset = (size[1] - new_height) // 2
            final_surface.blit(scaled_image, (x_offset, y_offset))

            return final_surface
        except:
            print(f"Unable to load image: {path}")
            surface = pygame.Surface(size)
            surface.fill((255, 0, 0))  # Red rectangle as a placeholder
            return surface

    @staticmethod
    def load_and_scale_ui(path: str, size: Tuple[int, int]) -> pygame.Surface:
        try:
            image = pygame.image.load(path)
            return pygame.transform.smoothscale(image, size)
        except:
            print(f"Unable to load image: {path}")
            surface = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(surface, (255, 0, 0, 128), surface.get_rect(), 1)  # Semi-transparent red border as a placeholder
            return surface