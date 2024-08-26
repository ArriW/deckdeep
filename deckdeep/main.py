import pygame
from deckdeep.game import Game
from deckdeep.config import SCREEN_WIDTH, SCREEN_HEIGHT
from deckdeep.logger import setup_game_logger

def main():
    # Initialize the logger
    logger = setup_game_logger(name='deckdeep_logger', log_file='deckdeep.log')
    logger.info("Starting D&D Deckbuilder", category="SYSTEM")

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("D&D Deckbuilder")
    
    game = Game(screen, logger)
    game.run()

    logger.info("Shutting down D&D Deckbuilder", category="SYSTEM")
    pygame.quit()

if __name__ == "__main__":
    main()