import random
from typing import List, Dict

class Card:
    def __init__(
        self,
        name: str,
        energy_cost: int,
        rarity: float,
        damage: int = 0,
        bonus_damage: int = 0,
        healing: int = 0,
        shield: int = 0,
        targets_all: bool = False,
        card_draw: int = 0,
        health_cost: int =0,
    ):
        self.name = name
        self.damage = damage
        self.bonus_damage = bonus_damage
        self.healing = healing
        self.shield = shield
        self.energy_cost = energy_cost
        self.rarity = rarity
        self.targets_all = targets_all
        self.card_draw = card_draw
        self.health_cost = health_cost

    @staticmethod
    def generate_card_pool(num_cards: int = 3) -> List["Card"]:
        card_pool = [
            Card("Draw Card", 1, 1, card_draw=1),
            Card("Boon", 0, 1, bonus_damage=2),
            Card("Fan of Kinves", 1,1, damage = 2, targets_all=True),
            Card("Cleave", 2, 1, damage=6, targets_all=True),
            Card("Major Heal", 2, 1, healing=15),
            Card("Fireball", 2, 0.7, damage=12, targets_all=True),
            Card("Ice Armor", 1, 0.7, shield=12,health_cost=4),
            Card("Foresight", 2, .7,shield=5,card_draw=2),
            Card("Lightning Strike", 2, 0.7, damage=10, bonus_damage=2),
            Card("Healing Potion", 2, 0.7, healing=15),
            Card("Defensive Stance", 2, 0.7, damage=5, shield=10),
            Card("Vampiric Touch", 2, 0.6, damage=8, healing=8),
            Card("Rage", 1, 0.8, bonus_damage=5,health_cost=5),
            Card("Poison Dagger", 1, 0.7, damage=6, bonus_damage=2),
            Card("Holy Light", 2, 0.6, healing=10, shield=5),
            # Card("Time Warp", 3, 0.4),
            Card("Earthquake", 3, 0.5, damage=15, targets_all=True),
            Card("Charm", 2, 0.6, shield=15,healing=3),
            Card("Whirlwind", 3, 0.7, damage=8, shield=3, targets_all=True),
            Card("Dragon's Breath", 4, 0.3, damage=20, targets_all=True),
            Card("Panic", 4 , 0.3, card_draw=5, health_cost=5),
            Card("Retreat", 4, 0.3, card_draw=2 , shield=15),
            Card("Barracade", 6 , 0.3, shield=60)
        ]
        return random.choices(
            card_pool, weights=[card.rarity for card in card_pool], k=num_cards
        )

    def to_dict(self) -> Dict:
        return {
            key: value for key, value in vars(self).items() if not key.startswith("_")
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Card":
        return cls(**data)

player_starting_deck = [
    Card("Quick Strike", 1, 1, damage=6),
    Card("Quick Strike", 1, 1, damage=6),
    Card("Quick Strike", 1, 1, damage=6),
    Card("Quick Strike", 1, 1, damage=6),
    Card("Boon", 0, 1, bonus_damage=4),
    Card("Boon", 0, 1, bonus_damage=4),
    Card("Shield", 1, 1, shield=8),
    Card("Shield", 1, 1, shield=8),
    Card("Shield", 1, 1, shield=8),
    Card("Heal", 1, 1, healing=8),
    Card("Power Strike", 2, 1, damage=15),
    Card("Draw Card", 1, 1, card_draw=1),
    Card("Draw Card", 1, 1, card_draw=1),
    Card("Cleave", 2, 1, damage=6, targets_all=True),
]