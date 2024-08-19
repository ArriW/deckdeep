import pygame

# Screen dimensions
SCREEN_WIDTH = 1450
SCREEN_HEIGHT = int(SCREEN_WIDTH * 2/3)

# Calibration
CALIBRATED_WIDTH = 1200

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BEIGE = (245, 245, 220)

# Scaling function
def scale(original_pixel_weight: int) -> int:
    return round(original_pixel_weight / CALIBRATED_WIDTH * SCREEN_WIDTH)

# Game constants
CARD_WIDTH = scale(160)
CARD_HEIGHT = scale(240)
CARD_SPACING = scale(10)
ICON_SIZE = scale(36)
PLAYER_SIZE = scale(100)

# Fonts
pygame.font.init()
FONT = pygame.font.Font(None, scale(26))
SMALL_FONT = pygame.font.Font(None, scale(23))
CARD_FONT = pygame.font.Font(None, scale(30))