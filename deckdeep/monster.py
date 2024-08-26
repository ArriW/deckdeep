import random
from typing import List, Dict, Callable
from deckdeep.config import scale
from deckdeep.status_effect import StatusEffectManager, Bleed, HealthRegain
import math

def asymptotic_scale(level:int, max_value:float, steepness=0.1):
    """
    Returns a value that asymptotically approaches max_value as level increases.
    The steepness parameter controls how quickly the value approaches max_value.
    Example) asymptotic_scale(10, 100, 0.1) returns 63.212055882855766
    Example) asymptotic_scale(20, 100, 0.1) returns 86.4662645136613
    Example) asymptotic_scale(10, 100, .15) returns 84.99999999999999
    Example) asymptotic_scale(20, 100, .15) returns 99.99999999999999
    Example) asymptotic_scale(10, 100, .3) returns 95.99999999999999
    Example) asymptotic_scale(20, 100, .3) returns 99.99999999999999
    """
    return max_value * (1 - math.exp(-steepness * level))
class MonsterAbility:
    def __init__(self, name: str, effect: Callable, probability: float):
        self.name = name
        self.effect = effect
        self.probability = probability

class MonsterType:
    def __init__(
        self,
        name: str,
        symbol: str,
        health_mult: float,
        damage_mult: float,
        rarity: float,
        abilities: List[MonsterAbility] = None
    ):
        self.name = name
        self.symbol = symbol
        self.health_mult = health_mult
        self.damage_mult = damage_mult
        self.rarity = rarity
        self.power = health_mult * damage_mult
        self.abilities = abilities or []

class Monster:
    monster_types: List[MonsterType] = [
        MonsterType("Goblin", "G", 0.7, 0.9, 1.0, [
            MonsterAbility("Sneak Attack", lambda m, t: t.take_damage(round(m.damage * (1 + asymptotic_scale(m.level, 0.3, 0.1)))), 0.5)
        ]),
        MonsterType("Zombie_1", "Z1", 0.4, 1.1, 1.0, [
            MonsterAbility("Infectious Bite", lambda m, t: t.status_effects.add_effect(Bleed(round(asymptotic_scale(m.level, 15, 0.15)))), 0.3)
        ]),
        MonsterType("Zombie_2", "Z2", 1.1, 0.5, 1.0, [
            MonsterAbility("Regenerate", lambda m, t: m.heal(round(m.max_health * asymptotic_scale(m.level, 0.4, 0.1))), 0.35)
        ]),
        MonsterType("Orc_1", "O1", 0.8, 0.8, 1.0, [
            MonsterAbility("Rage", lambda m, t: setattr(m, 'damage', round(m.damage * (1 + asymptotic_scale(m.level, 0.3, 0.1)))), 0.3),
            MonsterAbility("Shield Up", lambda m, t: m.grant_shields(round(m.max_health * asymptotic_scale(m.level, 0.3, 0.1))), 0.35)
        ]),
        MonsterType("Orc_2", "O2", 1.0, 0.6, 1.0, [
            MonsterAbility("Battle Cry", lambda m, t: m.heal(round(m.max_health * asymptotic_scale(m.level, 0.25, 0.1))), 0.3),
            MonsterAbility("Shield Up", lambda m, t: m.grant_shields(round(m.max_health * asymptotic_scale(m.level, 0.3, 0.1))), 0.35)
        ]),
        MonsterType("Witch", "W", 0.6, 1.1, 0.8, [
            MonsterAbility("Curse", lambda m, t: m.status_effects.add_effect(HealthRegain(round(asymptotic_scale(m.level, 15, 0.1)))), 0.35),
            MonsterAbility("Magic Shield", lambda m, t: m.grant_shields(round(m.max_health * asymptotic_scale(m.level, 0.4, 0.1))), 0.3)
        ]),
        MonsterType("Guardian_1", "G1", 1.3, 0.5, 0.7, [
            MonsterAbility("Fortify", lambda m, t: m.grant_shields(round(m.max_health * asymptotic_scale(m.level, .6, 0.1))), 0.4),
            MonsterAbility("Power over time", lambda m, t: setattr(m, 'damage', round(m.damage * (1 + asymptotic_scale(m.level, 0.2, 0.1)))), 0.4)
        ]),
        MonsterType("Guardian_2", "G2", 0.7, 0.9, 0.7, [
            MonsterAbility("Protect", lambda m, t: m.grant_shields(round(m.max_health * asymptotic_scale(m.level, 0.4, 0.1))), 0.35),
            MonsterAbility("Power over time", lambda m, t: setattr(m, 'damage', round(m.damage * (1 + asymptotic_scale(m.level, 0.2, 0.1)))), 0.4),
            MonsterAbility("Mend", lambda m, t: m.heal(round(m.max_health * asymptotic_scale(m.level, 0.2, 0.1))), 0.3)
        ]),
    ]

    boss_types: List[MonsterType] = [
        MonsterType("Troll", "T", 1.6, 0.9, 1.0, [
            MonsterAbility("Troll Regeneration", lambda m, t: m.heal(round(m.max_health * asymptotic_scale(m.level, 0.4, 0.1))), 0.35)
        ]),
        MonsterType("Dragon", "D", 1.4, 1.2, 1.0, [
            MonsterAbility("Fire Breath", lambda m, t: t.status_effects.add_effect(Bleed(round(asymptotic_scale(m.level, 20, 0.1)))), 0.3),
            MonsterAbility("Divine Shield", lambda m, t: m.grant_shields(round(m.max_health * asymptotic_scale(m.level, 0.5, 0.2))), 0.3)
        ]),
        MonsterType("Corrupted_Paladin", "CP", 1.1, 1.1, 1.0, [
            MonsterAbility("Corruption", lambda m, t: t.status_effects.add_effect(Bleed(round(asymptotic_scale(m.level, 30, 0.2)))), 0.3),
            MonsterAbility("Holy Light", lambda m, t: m.heal(round(m.max_health * asymptotic_scale(m.level, 0.5, 0.1))), 0.25),
            MonsterAbility("Divine Shield", lambda m, t: m.grant_shields(round(m.max_health * asymptotic_scale(m.level, 0.5, 0.2))), 0.3)
        ]),
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
        selected: bool = False,
        is_boss: bool = False,
        monster_type: MonsterType = None,
        shields: int = 0,
        level: int = 1
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
        self.is_boss = is_boss
        self.status_effects = StatusEffectManager()
        self.monster_type = monster_type
        self.shields = shields
        self.level = level

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> Dict:
        data = {
            key: value for key, value in vars(self).items() if not key.startswith("_")
        }
        data['status_effects'] = self.status_effects.to_dict()
        data['monster_type'] = self.monster_type.name if self.monster_type else None
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Monster":
        status_effects = data.pop('status_effects', {})
        monster_type_name = data.pop('monster_type', None)
        monster = cls(**data)
        monster.status_effects = StatusEffectManager.from_dict(status_effects)
        if monster_type_name:
            monster.monster_type = next((mt for mt in cls.monster_types + cls.boss_types if mt.name == monster_type_name), None)
        return monster

    def attack(self, target):
        target.take_damage(self.damage)

    def receive_damage(self, damage: int) -> int:
        if self.shields > 0:
            if damage > self.shields:
                remaining_damage = damage - self.shields
                self.shields = 0
                damage = remaining_damage
            else:
                self.shields -= damage
                return self.health  # No damage to health if fully absorbed by shields

        old_health = self.health
        self.health = self.health - damage
        actual_damage = old_health - self.health
        health_percentage = (actual_damage / self.max_health) * 100
        self.shake = round(min(health_percentage, 100))
        return self.health

    def grant_shields(self, amount: int):
        self.shields += amount

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def take_damage(self, damage: int) -> int:
        return self.receive_damage(damage)

    def apply_status_effects(self):
        self.status_effects.apply_effects(self)

    def decide_action(self, target)->str:
        if self.monster_type and self.monster_type.abilities:
            for ability in self.monster_type.abilities:
                if random.random() < ability.probability:
                    ability.effect(self, target)
                    return f"{self.name} uses {ability.name}!"
        
        # Default action: attack
        self.attack(target)
        return f"{self.name} attacks for {self.damage} damage."

    def get_power(self):
        return self.health * self.damage

    @classmethod
    def generate(cls, level: int) -> "Monster":
        weights = [1 / (mt.power**2) for mt in cls.monster_types]
        monster_type = random.choices(cls.monster_types, weights=weights)[0]
        monster_type = random.choices(cls.monster_types, weights=weights, k=1)[0]
        base_health = round(12 + level * 2)
        base_damage = round(4 + level * 1.2)
        max_health = round(base_health * monster_type.health_mult)
        damage = round(base_damage * monster_type.damage_mult)
        image_path = f"./assets/images/characters/{monster_type.name.lower()}.png"
        monster = cls(
            name=monster_type.name,
            max_health=max_health,
            damage=damage,
            image_path=image_path,
            symbol=monster_type.symbol,
            monster_type=monster_type
        )
        return monster

    @classmethod
    def generate_boss(cls, level: int) -> "Monster":
        boss_type = random.choice(cls.boss_types)
        base_health = round(20 + level * 4)
        base_damage = round(8 + level * 1.6)
        max_health = round(base_health * boss_type.health_mult)
        damage = round(base_damage * boss_type.damage_mult)
        image_path = f"./assets/images/characters/{boss_type.name.lower()}.png"
        monster = cls(
            name=f"Boss {boss_type.name}",
            max_health=max_health,
            damage=damage,
            image_path=image_path,
            symbol=boss_type.symbol,
            is_boss=True,
            size=300,  # Make the boss larger
            monster_type=boss_type
        )
        return monster
