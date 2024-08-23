import pygame
from deckdeep.game import Game
from deckdeep.config import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("D&D Deckbuilder")
    
    game = Game(screen)
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()