# D&D Deckbuilder

D&D Deckbuilder is a roguelike deck-building game implemented in Python using the Pygame library. Battle through a dungeon, defeat monsters, and build your deck as you progress!

## Table of Contents
1. [Installation](#installation)
2. [How to Play](#how-to-play)
3. [Game Mechanics](#game-mechanics)
4. [Controls](#controls)
5. [File Structure](#file-structure)
6. [Contributing](#contributing)

## Installation

1. Ensure you have Python 3.7+ installed on your system.
2. Install Pygame by running:
   ```
   pip install pygame
   ```
3. Clone this repository or download the source code.
4. Navigate to the game directory in your terminal.
5. Run the game using:
   ```
   python builder.py
   ```

## How to Play

1. Start the game by running `deck_builder.py`.
2. You'll begin with a basic deck of cards.
3. Each turn, draw cards from your deck and use them to attack monsters, gain shields, or heal.
4. Defeat monsters to progress through dungeon levels and increase your score.
5. After defeating a monster, choose a new card to add to your deck.
6. The game ends when your health reaches 0.

## Game Mechanics

- **Cards**: Each card has various effects such as dealing damage, providing shields, healing, or drawing more cards.
- **Energy**: You have a limited amount of energy each turn to play cards.
- **Monsters**: Each monster has unique health and damage values. Some are tougher than others!
- **Dungeon Levels**: As you progress, monsters become stronger, but so do you!
- **Deck Building**: After each victory, choose a new card to add to your deck, making your character stronger.

## Controls

- **Mouse**: Click on cards to select them, click again to play them.
- **Number Keys (1-0)**: Quickly select cards in your hand.
- **Enter**: Play the selected card.
- **E**: End your turn.
- **Left/Right Arrow Keys**: Navigate card choices after defeating a monster.
- **Space**: Skip adding a new card to your deck after a victory.

## File Structure

```
D&D_Deckbuilder/
│
├── main.py
├── README.md
├── images/
│   ├── player.png
│   ├── goblin.png
│   ├── orc.png
│   ├── troll.png
│   ├── dragon.png
│   └── witch.png
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
