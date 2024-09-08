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
## Controls

### General

| Key | Action |
|-----|--------|
| SPACE | End turn |
| ESC | Open/close menu |
| 1 | View deck |
| 2 | View relics |

### Card Selection

| Key | Action |
|-----|--------|
| Q, W, E, R, T, Y, U, I, O, P | Select and play cards in your hand |

### Combat

| Key | Action |
|-----|--------|
| H | Select previous monster |
| L | Select next monster |

### Event

| Key | Action |
|-----|--------|
| Q, W, E, R, T, Y, U, I, O, P | Select event options |

### Deck View

| Key | Action |
|-----|--------|
| H | Previous page |
| L | Next page |
| ESC | Close deck view |

### Relic View

| Key | Action |
|-----|--------|
| ESC or 2 | Close relic view |

### Victory Screen

| Key | Action |
|-----|--------|
| Q, W, E | Select new card |
| R | Skip card selection (gain +5 max HP) |

### Node Selection

| Key | Action |
|-----|--------|
| Q, W, E, R, T, Y, U, I, O, P | Select next node |

