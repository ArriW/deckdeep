import random
from typing import List, Dict
from enum import Enum
from deckdeep.custom_types import Energy


class Rarity(Enum):
    COMMON = 1.0
    UNCOMMON = 0.8
    RARE = 0.7
    UNIQUE = 0.6
    LEGENDARY = 0.5


class Card:
    def __init__(
        self,
        name: str,
        energy_cost: int,
        rarity: Rarity,
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
        weakness: int = 0,
        bolster: int = 0,
        burn: int = 0,
        cleanse: bool = False,
        num_attacks: int = 1,  # New attribute for multi-attack
    ):
        self.name = name
        self.energy_cost = Energy(energy_cost)
        self.damage = int(damage)
        self.bonus_damage = int(bonus_damage)
        self.healing = int(healing)
        self.shield = int(shield)
        self.rarity = rarity if isinstance(rarity, Rarity) else Rarity(rarity)
        self.targets_all = bool(targets_all)
        self.card_draw = int(card_draw)
        self.health_cost = int(health_cost)
        self.bleed = int(bleed)
        self.energy_bonus = int(energy_bonus)
        self.health_regain = int(health_regain)
        self.weakness = weakness
        self.bolster = bolster
        self.burn = burn
        self.cleanse = cleanse
        self.num_attacks = num_attacks

        # Animation properties
        self.x = 0
        self.y = 0
        self.opacity = 255
        self.is_animating = False

    def start_animation(self, start_x: int, start_y: int):
        self.x = start_x
        self.y = start_y
        self.opacity = 255
        self.is_animating = True

    def update_animation(self, speed: int = 5, fade_speed: int = 10):
        if self.is_animating:
            self.y -= speed
            # pygame.time.wait(50)
            self.opacity = max(0, self.opacity - fade_speed)
            if self.opacity == 0:
                self.is_animating = False

    def reset_animation(self):
        # self.is_animating = True
        self.opacity = (
            255  # Reset opacity or any other properties involved in animation
        )

    @staticmethod
    def generate_card_pool(num_cards: int = 3) -> List["Card"]:
        card_pool = [
            Card("Weaken", 1, Rarity.UNCOMMON, weakness=4),
            Card("Fortify", 1, Rarity.COMMON, bolster=3),
            Card("Ignite", 2, Rarity.UNCOMMON, damage=5, burn=3),
            Card("Kindling", 1, Rarity.COMMON, damage=3, burn=1),
            Card("Poison Dart", 1, Rarity.COMMON, damage=3, bleed=3),
            Card("Mana Surge", 1, Rarity.UNCOMMON, energy_bonus=1, card_draw=1),
            Card("Life Tap", 1, Rarity.UNCOMMON, card_draw=2, health_cost=5),
            Card("Earthquake", 3, Rarity.RARE, damage=8, targets_all=True, shield=5),
            Card("Inspire", 2, Rarity.UNCOMMON, bonus_damage=3, card_draw=1, healing=5),
            Card("Blood Pact", 4, Rarity.RARE, damage=20, health_cost=10, bleed=5),
            Card("Meditation", 1, Rarity.COMMON, shield=5, health_regain=2),
            Card(
                "Chain Lightning",
                3,
                Rarity.RARE,
                damage=12,
                targets_all=True,
                energy_bonus=1,
            ),
            Card("Soul Shred", 2, Rarity.UNCOMMON, damage=8, healing=4, bleed=2),
            Card("Fortify", 2, Rarity.UNCOMMON, shield=10, bolster=2),
            Card("Rage", 1, Rarity.COMMON, bonus_damage=5, health_cost=3),
            Card("Time Warp", 3, Rarity.UNIQUE, card_draw=3, energy_bonus=1),
            Card("Venomous Strike", 2, Rarity.UNCOMMON, damage=7, bleed=4),
            Card("Arcane Missile", 1, Rarity.COMMON, damage=3, targets_all=True),
            Card("Drain", 3, Rarity.RARE, damage=10, health_regain=4, weakness=2),
            Card("Major Heal", 2, Rarity.UNCOMMON, healing=15),
            Card("Charm", 2, Rarity.UNCOMMON, shield=15, healing=3),
            Card("Revive", 9, Rarity.LEGENDARY, healing=100),
            Card(
                "Overload", 3, Rarity.RARE, damage=15, health_cost=10, targets_all=True
            ),
            Card("Healing Potion", 2, Rarity.COMMON, healing=10, health_regain=3),
            Card("Crooked Trade", 1, Rarity.UNCOMMON, health_cost=5, bonus_damage=5),
            Card("Ice Armor", 3, Rarity.UNCOMMON, shield=15, weakness=2),
            Card("Hidden Dagger", 1, Rarity.COMMON, damage=6, bleed=2),
            Card("Lacerate", 1, Rarity.COMMON, bleed=4),
            Card("Barricade", 6, Rarity.UNIQUE, shield=60),
            Card("Battle Stance", 2, Rarity.UNCOMMON, damage=5, shield=8, bolster=1),
            Card("Power Strike", 2, Rarity.COMMON, damage=15),
            Card("Holy Light", 2, Rarity.UNCOMMON, healing=10, shield=5),
            Card(
                "Fan of Knives", 1, Rarity.UNCOMMON, damage=1, targets_all=True, bleed=2
            ),
            Card("Boon", 0, Rarity.COMMON, bonus_damage=2),
            Card("Exchange", 2, Rarity.UNCOMMON, bleed=3, health_regain=3),
            Card("Patience", 1, Rarity.UNCOMMON, bonus_damage=3, card_draw=1),
            Card("Cleave", 2, Rarity.UNCOMMON, damage=6, targets_all=True),
            Card(
                "Whirlwind",
                3,
                Rarity.RARE,
                damage=2,
                shield=3,
                targets_all=True,
                bleed=2,
            ),
            Card("Fireball", 4, Rarity.RARE, damage=12, burn=3, targets_all=True),
            Card("Vampiric Touch", 2, Rarity.UNCOMMON, damage=8, healing=8),
            Card("Trap Door", 4, Rarity.RARE, bleed=15, bonus_damage=3),
            Card("Panic!", 1, Rarity.RARE, card_draw=5, health_cost=20),
            Card("Regeneration", 2, Rarity.UNIQUE, health_regain=5),
            Card("Foresight", 2, Rarity.UNCOMMON, shield=5, card_draw=2),
            Card(
                "Monstrosity",
                2,
                Rarity.UNIQUE,
                health_regain=5,
                health_cost=10,
                bonus_damage=4,
            ),
            Card("Retreat.", 5, Rarity.RARE, card_draw=4, shield=15),
            Card(
                "Lightning", 4, Rarity.RARE, damage=10, bonus_damage=2, targets_all=True
            ),
            Card("Culling", 4, Rarity.RARE, damage=25, bleed=5),
            Card(
                "Dragon Fire", 6, Rarity.LEGENDARY, damage=25, burn=5, targets_all=True
            ),
            Card(
                "@allcosts",
                1,
                Rarity.LEGENDARY,
                energy_bonus=2,
                health_cost=20,
                bonus_damage=6,
            ),
            Card("Flame Burst", 2, Rarity.UNCOMMON, damage=8, burn=2),
            Card("Devestating Strike", 5, Rarity.UNCOMMON, damage=40),
            Card("Inferno", 4, Rarity.RARE, damage=12, burn=4, targets_all=True),
            Card("Ember Shield", 5, Rarity.UNCOMMON, shield=20, burn=1),
            Card("Rally Troops", 2, Rarity.UNCOMMON, bolster=3, card_draw=1),
            Card("Warcry", 2, Rarity.RARE, bolster=2, bonus_damage=4, targets_all=True),
            Card("Defensive Stance", 1, Rarity.COMMON, shield=8, bolster=1),
            Card("Double Strike", 1, Rarity.UNCOMMON, damage=3, num_attacks=2),
            Card("Triple Slash", 2, Rarity.RARE, damage=5, num_attacks=3),
            Card("Flurry of Blows", 1, Rarity.COMMON, damage=2, num_attacks=2),
        ]
        return random.choices(
            card_pool, weights=[card.rarity.value for card in card_pool], k=num_cards
        )

    def to_dict(self) -> Dict:
        return {
            key: (value.value if key == "rarity" else value)
            for key, value in vars(self).items()
            if not key.startswith("_")
            and not key == "is_animating"
            and not key == "x"
            and not key == "y"
            and not key == "opacity"
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Card":
        if isinstance(data["rarity"], (int, float)):
            data["rarity"] = Rarity(data["rarity"])
        elif isinstance(data["rarity"], str):
            data["rarity"] = Rarity[data["rarity"]]
        return cls(**data)

    def calculate_total_damage(
        self, player_bonus_damage: int, player_strength: int
    ) -> int:
        if self.damage == 0:
            return 0

        base_damage = self.damage + self.bonus_damage
        total_damage = (
            base_damage + player_strength + player_bonus_damage
        ) * self.num_attacks
        return total_damage


def get_player_starting_deck() -> List[Card]:
    return [
        Card("Quick Strike", 1, Rarity.COMMON, damage=6),
        Card("Quick Strike", 1, Rarity.COMMON, damage=6),
        Card("Quick Strike", 1, Rarity.COMMON, damage=6),
        Card("Quick Strike", 1, Rarity.COMMON, damage=6),
        Card("Soulful Persuit", 0, Rarity.COMMON, bonus_damage=2),
        Card("Soulful Persuit", 0, Rarity.COMMON, bonus_damage=2),
        Card("Shield", 1, Rarity.COMMON, shield=6),
        Card("Shield", 1, Rarity.COMMON, shield=6),
        Card("Shield", 1, Rarity.COMMON, shield=6),
        Card("Shield", 1, Rarity.COMMON, shield=6),
        Card("Power Strike", 2, Rarity.COMMON, damage=15),
        Card("Double Strike", 1, Rarity.UNCOMMON, damage=3, num_attacks=2),
        Card("Awals Gift", 0, Rarity.COMMON, card_draw=1, health_regain=2, healing=3),
    ]
