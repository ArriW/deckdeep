import pygame

# Screen dimensions
SCREEN_WIDTH = 1450
SCREEN_HEIGHT = int(SCREEN_WIDTH * 2 / 3)

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
PURPLE = (128, 0, 128)


# Scaling function
def scale(original_pixel_weight: int) -> int:
    return round(original_pixel_weight / CALIBRATED_WIDTH * SCREEN_WIDTH)


# Game constants
CARD_WIDTH = scale(160)
CARD_HEIGHT = scale(240)
CARD_SPACING = scale(10)
ICON_SIZE = scale(36)
PLAYER_SIZE = scale(130)

# Fonts
pygame.font.init()
FONT = pygame.font.Font(None, scale(26))
SMALL_FONT = pygame.font.Font(None, scale(23))
CARD_FONT = pygame.font.Font(None, scale(30))


HEADER_HEIGHT = scale(50)
END_TURN_BUTTON_X = SCREEN_WIDTH - scale(120)
END_TURN_BUTTON_Y = HEADER_HEIGHT + scale(60)
VIEW_DECK_BUTTON_X = SCREEN_WIDTH - scale(120)
VIEW_DECK_BUTTON_Y = HEADER_HEIGHT + scale(110)
BUTTON_WIDTH = scale(100)
BUTTON_HEIGHT = scale(40)

# Keybinds
KEYBINDS = {
    "General": {
        "ESCAPE": "Open/close menu",
        "SPACE": "End turn",
        "1": "View deck",
        "2": "View relics",
        "3": "View keybinds",
    },
    "Card Selection": {
        "Q, W, E, R, T, Y, U, I, O, P": "Select and play cards in your hand",
    },
    "Relic Selection": {
        "Q, W, E, R, T, Y, U, I, O, P": "Select relics after boss victory",
    },
    "Combat": {
        "H": "Select previous monster",
        "L": "Select next monster",
    },
    "Event": {
        "Q, W, E, R, T, Y, U, I, O, P": "Select event options",
    },
    "Deck View": {
        "H": "Previous page",
        "L": "Next page",
        "ESCAPE": "Close deck view",
    },
    "Relic View": {
        "ESCAPE, 2": "Close relic view",
    },
    "Victory Screen": {
        "Q, W, E, R": "Select new card or skip",
    },
    "Node Selection": {
        "Q, W, E, R, T, Y, U, I, O, P": "Select next node",
    },
    "Menu": {
        "K": "Select previous option",
        "J": "Select next option",
        "SPACE": "Execute selected option",
        "ESCAPE": "Close menu",
    },
}
