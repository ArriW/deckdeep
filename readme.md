# DeckDeep Deckbuilder

![DeckDeep Deckbuilder Background](/assets/images/backgrounds/background.png)

DeckDeep Deckbuilder is a roguelike deck-building game implemented in Python using the Pygame library. Battle through a dungeon, defeat monsters, and build your deck as you progress!

## Table of Contents
1. [Installation](#installation)
2. [How to Play](#how-to-play)
3. [Game Mechanics](#game-mechanics)
4. [Controls](#controls)
5. [Project Structure](#project-structure)
6. [Contributing](#contributing)
7. [Attribution](#attribution)

## Installation

1. Ensure you have Python 3.7+ installed on your system.
2. Install dependencies
   ```
   pip install -r requirements.txt
   ```
3. Clone this repository or download the source code.
4. Navigate to the game directory in your terminal.
5. Run the game using:
   ```
   python -m deckdeep.main
   ```

## How to Play

1. Start the game by running `python -m deckdeep.main`.
2. You'll begin with a basic deck of cards.
3. Each turn, draw cards from your deck and use them to attack monsters, gain shields, or heal.
4. Defeat monsters to progress through dungeon levels and increase your score.
5. After defeating a monster, choose a new card to add to your deck from a selection of three random cards.
6. The game ends when your health reaches 0.

![Gameplay](/assets/images/backgrounds/gp_screenshot.png)

## Game Mechanics

- **Cards**: Each card has various effects such as dealing damage, providing shields, healing, or drawing more cards. Cards now have visual icons representing their attributes.
- **Energy**: You have a limited amount of energy each turn to play cards. Your energy is represented by a blue bar.
- **Health**: Your health is represented by a green bar. The monster's health is represented by a red bar.
- **Monsters**: Each monster has unique health and damage values. Some are tougher than others!
- **Dungeon Levels**: As you progress, monsters become stronger, but so do you!
- **Deck Building**: After each victory, choose a new card to add to your deck from a selection of three, making your character stronger.
- **Card Rarity**: New cards have different rarities, affecting how often they appear as choices after a victory.

## Controls

- **Mouse**: Click on cards to select them, click again to play them. Click on "End Turn" or "Discard" buttons.
- **Number Keys (1-9)**: Quickly select and play cards in your hand.
- **E**: End your turn.
- **Arrow Keys**: Select targets for your attacks.
- **Number Keys (1-3)**: Select a new card after defeating a monster.
- **Space**: Skip adding a new card to your deck after a victory.

## Project Structure

The game code is now organized in the `deckdeep` package:

- `deckdeep/main.py`: Entry point of the game
- `deckdeep/game.py`: Contains the main Game class and game loop
- `deckdeep/config.py`: Game constants and configuration
- `deckdeep/assets.py`: Asset management
- `deckdeep/player.py`: Player class definition
- `deckdeep/monster.py`: Monster and MonsterType class definitions
- `deckdeep/monster_group.py`: MonsterGroup class for managing multiple monsters
- `deckdeep/card.py`: Card class definition and card pool generation
- `deckdeep/music_manager.py`: Background music management
- `deckdeep/render.py`: Rendering functions for game elements

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Attribution

**Album:** Destruction Bringer (Free)  
**Artist:** [One Man Symphony](https://onemansymphony.bandcamp.com)  
**Description:** A heavy/progressive metal album with 10 tracks, inspired by Mick Gordon's Doom (2016) and Doom Eternal (2020) soundtracks. The tracks are designed to facilitate seamless transitions in scenes, making them suitable for various media, especially in gaming.

### Track Themes:
- **Six Boss Fight Themes**
- **Three Regular Encounter Themes** (suitable for any battle)
- **One Main Menu Theme**

**Additional Content:** Bonus and extended tracks, along with loop files, are available on the artist's [Patreon page](https://www.patreon.com/onemansymphony).

This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
