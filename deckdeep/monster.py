import random
from typing import List, Dict
from deckdeep.config import scale

class MonsterType:
    def __init__(
        self,
        name: str,
        symbol: str,
        health_mult: float,
        damage_mult: float,
        rarity: float
    ):
        self.name = name
        self.symbol = symbol
        self.health_mult = health_mult
        self.damage_mult = damage_mult
        self.rarity = rarity
        self.power = health_mult * damage_mult

class Monster:
    monster_types: List[MonsterType] = [
        MonsterType("Goblin", "G", 0.6, 0.6, 1.0),
        MonsterType("Zombie_1", "Z1", 0.3, 1.2, 1.0),
        MonsterType("Zombie_2", "Z2", 1, 0.3, 1.0),
        MonsterType("orc_2", "O", 0.9, 0.7, 1.0),
        MonsterType("orc_1", "O", 0.7, 0.9, 1.0),
        MonsterType("Troll", "T", 1.2, 1.1, 0.6),
        MonsterType("Dragon", "D", 1.5, 1.5, 0.3),
        MonsterType("Witch", "W", 0.6, 1.2, 0.5),
    ]

    def __init__(
        self,
        name: str,
        max_health: int,
        damage: int,
        image_path: str,
        symbol: str = "",
        health: int = None,
        size: int = 100,
        shake: int = 0,
        selected: bool = False
    ):
        self.name = name
        self.max_health = max_health
        self.health = health if health is not None else max_health
        self.damage = damage
        self.image_path = image_path
        self.symbol = symbol
        self.size = scale(size)
        self.shake = shake
        self.selected = selected

    def to_dict(self) -> Dict:
        return {
            key: value for key, value in vars(self).items() if not key.startswith("_")
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Monster":
        return cls(**data)

    def attack(self, target):
        target.take_damage(self.damage)

    def receive_damage(self, damage: int) -> int:
        old_health = self.health
        self.health = max(0, self.health - damage)
        actual_damage = old_health - self.health
        health_percentage = (actual_damage / self.max_health) * 100
        self.shake = round(min(health_percentage, 100))
        return self.health  # Return remaining health

    @classmethod
    def generate(cls, level: int) -> "Monster":
        weights = [1 / (mt.power**2) for mt in cls.monster_types]
        monster_type = random.choices(cls.monster_types, weights=weights)[0]
        base_health = round(10 + level * 2)
        base_damage = round(4 + level * 1.2)
        max_health = round(base_health * monster_type.health_mult)
        damage = round(base_damage * monster_type.damage_mult)
        image_path = f"./assets/images/characters/{monster_type.name.lower()}.png"
        return cls(
            name=monster_type.name,
            max_health=max_health,
            damage=damage,
            image_path=image_path,
            symbol=monster_type.symbol
        )