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
        health_cost: int = 0,
        bleed: int = 0,
        energy_bonus: int = 0,
        health_regain: int = 0,
    ):
        self.name = name
        self.damage = int(damage) 
        self.bonus_damage = int(bonus_damage)
        self.healing = int(healing)
        self.shield = int(shield)
        self.energy_cost = int(energy_cost)
        self.rarity = float(rarity)
        self.targets_all = bool(targets_all)
        self.card_draw = int(card_draw)
        self.health_cost = int(health_cost)
        self.bleed = int(bleed)
        self.energy_bonus = int(energy_bonus)
        self.health_regain = int(health_regain)

    @staticmethod
    def generate_card_pool(num_cards: int = 3) -> List["Card"]:
        card_pool = [
            # Unclassified

            Card("Poison Dart", 1, 0.8, damage=3, bleed=3),
            Card("Mana Surge", 1, 0.6, energy_bonus=1, card_draw=1),
            Card("Life Tap", 1, 0.7, card_draw=2, health_cost=5),
            Card("Earthquake", 3, 0.5, damage=8, targets_all=True, shield=5),
            Card("Inspire", 2, 0.6, bonus_damage=3, card_draw=1, healing=5),
            Card("Blood Pact", 4, 0.4, damage=20, health_cost=10, bleed=5),
            Card("Meditation", 1, 0.7, shield=8, health_regain=2),
            Card("Chain Lightning", 3, 0.5, damage=12, targets_all=True, energy_bonus=1),
            Card("Siphon Soul", 2, 0.6, damage=8, healing=4, bleed=2),
            Card("Fortify", 2, 0.7, shield=12, bonus_damage=2),
            Card("Rage", 1, 0.6, bonus_damage=5, health_cost=3),
            Card("Time Warp", 3, 0.3, card_draw=3, energy_bonus=1),
            Card("Venomous Strike", 2, 0.7, damage=7, bleed=4),
            Card("Arcane Missile", 1, 0.8, damage=3, targets_all=True),
            Card("Soul Drain", 3, 0.5, damage=10, healing=10, health_cost=5),

            # F

            # D

            # C
            Card("Major Heal", 2, .9, healing=15),
            Card("Charm", 2, 0.6, shield=15, healing=3),
            Card("Revive",9,.3,healing=100),
            Card("Overload", 3, 0.7, damage=15, health_cost=10, targets_all=True),

            Card("Healing Potion", 2, 0.7, healing=10,health_regain=3),
            # B
            Card("Crooked Trade",1,0.8,health_cost=5,bonus_damage=5),
            Card("Ice Armor", 1, 0.7, shield=15, health_cost=4),
            Card("Hidden Dagger", 1, 1, damage=6, bleed=2),
            Card("Lacerate", 1, 1, bleed=4),
            Card("Barricade", 6, .2, shield=60),
            Card("Defensive Stance", 2, 1, damage=5, shield=10),
            Card("Power Strike", 2, 1, damage=15),
            Card("Holy Light", 2, 0.7, healing=10, shield=5),
            Card("Fan of Knives", 1, 1, damage=1, targets_all=True, bleed=1),
            Card("Boon", 0, 1, bonus_damage=2),
            Card("Equivalent Exchange",2,.7,bleed=3,health_regain=3),
            
            
            # A
            Card("Patience", 1, .7, bonus_damage=3, card_draw=1),
            Card("Cleave", 2, .9, damage=6, targets_all=True),
            Card("Whirlwind", 3, 0.7, damage=2, shield=3, targets_all=True, bleed=2),
            Card("Fireball", 4, 0.7, damage=14, targets_all=True),
            Card("Vampiric Touch", 2, .7, damage=8, healing=8),
            Card("Trap Door",4,0.6, bleed=18,bonus_damage=3),
            
            # S
            Card("Panic!",3, 0.5, card_draw=3, health_cost=15),
            Card("Regeneration", 2, 0.3, health_regain=5),
            Card("Foresight", 2, .7, shield=5, card_draw=2),
            Card("Frienzied Regeneration", 2, 0.3, health_regain=5,health_cost=10,bonus_damage=4),
            Card("Retreat.", 5, 0.5, card_draw=4, shield=15),
            Card("Lightning Strike", 4, 0.7, damage=10, bonus_damage=2,targets_all=True),
            Card("Culling", 4, 0.7, damage=25,bleed=5),

            # SS
            Card("Dragon's Breath", 5, 0.3, damage=30, targets_all=True),
            Card("@allcosts", 1, 0.3, energy_bonus=2, health_cost=20,bonus_damage=6),
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

def get_player_starting_deck()-> List[Card]:
    return [
    Card("Quick Strike", 1, 1, damage=6),
    Card("Quick Strike", 1, 1, damage=6),
    Card("Quick Strike", 1, 1, damage=6),
    Card("Quick Strike", 1, 1, damage=6),
    Card("Soulful Persuit", 0, 1, bonus_damage=2),
    Card("Soulful Persuit", 0, 1, bonus_damage=2),
    Card("Shield", 1, 1, shield=6),
    Card("Shield", 1, 1, shield=6),
    Card("Shield", 1, 1, shield=6),
    Card("Shield", 1, 1, shield=6),
    Card("Power Strike", 2, 1, damage=15),
    Card("AW's Gift", 0, 1, card_draw=1,health_regain=1, healing=3),
]