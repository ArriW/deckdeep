from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import random
import math
from deckdeep.status_effect import StatusEffectManager, Bleed, HealthRegain
from deckdeep.config import scale

from enum import Enum

class IconType(Enum):
    ATTACK = 1
    DEFEND = 2
    BUFF = 3
    BLEED = 4
    HEAL = 5
    MAGIC = 6
    UNKNOWN = 7

class Ability(ABC):
    def __init__(self, name: str, probability: float, icon_types: List[IconType]):
        self.name = name
        self.probability = probability
        self._power_contribution = 0
        self.icon_types = icon_types

    @abstractmethod
    def use(self, user, target):
        pass

    @abstractmethod
    def calculate_power_contribution(self, user):
        pass

    @property
    def power_contribution(self):
        return self._power_contribution

    @power_contribution.setter
    def power_contribution(self, value):
        self._power_contribution = value

class BasicAttack(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK])
    def use(self, user, target):
        damage = user.damage
        target.take_damage(damage)
        return f"{user.name} attacks for {damage} damage!"
    def calculate_power_contribution(self, user):
        return user.damage

class SneakAttack(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK])
    def use(self, user, target):
        damage = round(user.damage * 1.5)
        target.take_damage(damage)
        return f"{user.name} performs a Sneak Attack for {damage} damage!"
    def calculate_power_contribution(self, user):
        return round(user.damage * 1.5)

class InfectiousBite(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK,IconType.BLEED])
    def use(self, user, target):
        target.take_damage(user.damage*.25)
        bleed_damage = max(round(user.damage * 0.25),3)
        bleed = Bleed(bleed_damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} inflicts an Infectious Bite, causing {bleed_damage} Bleed!"
    def calculate_power_contribution(self, user):
        return max(round(user.damage * 0.25),3)

class Rage(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.BUFF, IconType.ATTACK])
    def use(self, user, target):
        old_damage = user.damage
        user.damage = round(user.damage * 1.2)
        return f"{user.name} enters a Rage, increasing damage from {old_damage} to {user.damage}!"
    def calculate_power_contribution(self, user):
        return round(user.damage * 0.2)

class BattleCry(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.HEAL])
    def use(self, user, target):
        heal_amount = round(user.spell_power * 0.5)
        user.heal(heal_amount)
        return f"{user.name} uses Battle Cry, healing for {heal_amount}!"
    def calculate_power_contribution(self, user):
        return round(user.spell_power * 0.5)

class ShieldUp(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.DEFEND])
    def use(self, user, target):
        shield_amount = round(user.max_health * 0.3)
        user.grant_shields(shield_amount)
        return f"{user.name} uses Shield Up, gaining {shield_amount} shields!"
    def calculate_power_contribution(self, user):
        return round(user.max_health * 0.3)

class Regenerate(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.HEAL])
    def use(self, user, target):
        heal_amount = round(user.max_health * 0.25)
        user.heal(heal_amount)
        return f"{user.name} Regenerates, healing for {heal_amount}!"
    def calculate_power_contribution(self, user):
        return round(user.max_health * 0.25)

class Fortify(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.DEFEND])
    def use(self, user, target):
        shield_amount = round(user.max_health * 0.2)
        user.grant_shields(shield_amount)
        return f"{user.name} Fortifies, gaining {shield_amount} shields!"
    def calculate_power_contribution(self, user):
        return round(user.max_health * 0.2)

class PowerOverTime(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK,IconType.BUFF])
    def use(self, user, target):
        old_damage = user.damage
        damage_dealt = round(user.damage)
        user.damage = round(user.damage * 1.2)
        target.take_damage(damage_dealt)
        return f"{user.name}'s power increases from {old_damage} to {user.damage} and deals {damage_dealt} damage!"
    def calculate_power_contribution(self, user):
        return round(user.damage * 0.2) + user.damage

class Curse(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.MAGIC, IconType.BLEED])
    def use(self, user, target):
        bleed_damage = round(user.spell_power * 0.3)
        bleed = Bleed(bleed_damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} Curses the target, causing {bleed_damage} Bleed!"
    def calculate_power_contribution(self, user):
        return round(user.spell_power * 0.3)

class MagicMissile(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.MAGIC])
    def use(self, user, target):
        damage = round(user.spell_power)
        target.take_damage(damage)
        return f"{user.name} casts Magic Missile for {damage} damage!"
    def calculate_power_contribution(self, user):
        return round(user.spell_power)

class TrollRegeneration(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.HEAL, IconType.BUFF])
    def use(self, user, target):
        heal_amount = round(user.max_health * 0.1)
        regen_amount = round(user.spell_power * 0.3)
        user.heal(heal_amount)
        regen = HealthRegain(regen_amount)
        user.status_effects.add_effect(regen)
        return f"{user.name} uses Troll Regeneration, healing for {heal_amount} and gaining {regen_amount} Health Regeneration!"
    def calculate_power_contribution(self, user):
        return round(user.max_health * 0.1) + round(user.spell_power * 0.3)

class FireBreath(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.BLEED])
    def use(self, user, target):
        damage = round(user.spell_power * 1.5)
        bleed = Bleed(v:=round(damage * 0.1))
        target.take_damage(damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} breathes fire for {damage} damage and inflicts {v} Bleed!"
    def calculate_power_contribution(self, user):
        damage = round(user.spell_power * 1.5)
        return damage + round(damage * 0.1)

class Corruption(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.BLEED])
    def use(self, user, target):
        user.spell_power += round(user.spell_power * 0.2)
        bleed_damage = round(user.spell_power * 0.3)
        bleed = Bleed(bleed_damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} corrupts the target, causing {bleed_damage} Bleed!"
    def calculate_power_contribution(self, user):
        return round(user.spell_power * 0.3)

class HolyLight(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.HEAL])
    def use(self, user, target):
        heal_amount = round(user.max_health * 0.3)
        user.heal(heal_amount)
        return f"{user.name} uses Holy Light, healing for {heal_amount}!"
    def calculate_power_contribution(self, user):
        return round(user.max_health * 0.3)

class DivineShield(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.DEFEND])
    def use(self, user, target):
        shield_amount = round(user.max_health * 0.4)
        user.grant_shields(shield_amount)
        return f"{user.name} gains a Divine Shield of {shield_amount}!"
    def calculate_power_contribution(self, user):
        return round(user.max_health * 0.4)

class PoisonDart(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.BLEED])
    def use(self, user, target):
        damage = round(user.spell_power * 0.5)
        target.take_damage(damage)
        return f"{user.name} fires a Poison Dart for {damage} damage and applies Weakness!"
    def calculate_power_contribution(self, user):
        return round(user.spell_power * 0.5) + 4  # Estimating the value of weakness

class ThunderClap(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.BUFF])
    def use(self, user, target):
        raise NotImplementedError("ThunderClap is not implemented yet")
    def calculate_power_contribution(self, user):
        return round(user.damage * 0.8 * 1.25)  # Estimating the value of vulnerable

class LifeDrain(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.HEAL])
    def use(self, user, target):
        damage = round(user.spell_power * 0.7)
        heal = round(damage * 0.5)
        target.take_damage(damage)
        user.heal(heal)
        return f"{user.name} uses Life Drain, dealing {damage} damage and healing for {heal}!"
    def calculate_power_contribution(self, user):
        damage = round(user.spell_power * 0.7)
        return damage + round(damage * 0.5)

class MonsterType:
    def __init__(
        self,
        name: str,
        symbol: str,
        health_mult: float,
        damage_mult: float,
        spell_power_mult: float,
        rarity: float,
        abilities: List[Ability] = None,
    ):
        self.name = name
        self.symbol = symbol
        self.health_mult = health_mult
        self.damage_mult = damage_mult
        self.spell_power_mult = spell_power_mult
        self.rarity = rarity
        self.abilities = abilities or []

class Monster:
    monster_types: List[MonsterType] = [
        MonsterType("Goblin", "G", 0.7, 0.9, 0.6, 1.0, [SneakAttack("Sneak Attack", 0.5), PoisonDart("Poison Dart", 0.3)]),
        MonsterType("Zombie_1", "Z", 0.8, 1.0, 0.3, 1.0, [InfectiousBite("Infectious Bite", 0.7),BasicAttack("Claw", 0.3)]),
        MonsterType("Zombie_1", "Z", 0.8, 1.0, 0.3, 1.0, [InfectiousBite("Infectious Bite", 0.7),BasicAttack("Claw", 0.3)]),
        MonsterType("Zombie_3", "Z", 0.3, 0.3, 0.3, 1.0, [InfectiousBite("Infectious Bite", 0.7),BasicAttack("Claw", 0.3)]),
        MonsterType("Zombie_4", "Z", 0.3, 0.3, 0.3, 1.0, [InfectiousBite("Infectious Bite", 0.7),BasicAttack("Claw", 0.3)]),
        MonsterType("Orc_1", "O", 0.9, 1.1, 0.7, 0.8, [Rage("Rage", 0.4), BasicAttack("Axe Attack", 0.6)]),
        MonsterType("Orc_2", "O", 1.1, 0.9, 0.7, 0.8, [BattleCry("Battle Cry", 0.3), ShieldUp("Block",0.2),BasicAttack("Axe Attack", 0.5)]),
        MonsterType("Troll", "T", 1.3, 1.1, 0.8, 0.6, [Regenerate("Regenerate", 0.35), BasicAttack("Fist", 0.65)]),
        MonsterType("Witch", "W", 0.6, 0.6, 1.2, 0.7, [Curse("Curse", 0.5), MagicMissile("Magic Missile", 0.4), LifeDrain("Life Drain", 0.3),BasicAttack("Staff Attack", 0.3)]),
        MonsterType("Guardian_1", "GL", 1.5, 0.7, 0.5, 0.5, [BasicAttack("Sword Attack",.6), ShieldUp("Shield Up", 0.3),PowerOverTime("Power over time", 0.1)]),
        MonsterType("Guardian_2", "D", 0.7, 1.2, 1.0, 0.4, [FireBreath("Fire Breath", 0.3), Corruption("Corruption", 0.4), LifeDrain("Life Drain", 0.3)]),
    ]

    boss_types: List[MonsterType] = [
        MonsterType("Troll", "TK", 2.4, 1.4, 1.0, 1.0, [TrollRegeneration("Troll Regeneration", 0.25), PowerOverTime("Power over time", 0.2), BasicAttack("Sword Attack", 0.55)]),
        MonsterType("Dragon", "DR", 1.8, 1.6, 1.3, 1.0, [FireBreath("Fire Breath", 0.25), Fortify("Fortify", 0.2), BasicAttack("Claw Attack", 0.35)]),
        MonsterType("Corrupted Paladin", "CP", 1.5, 1.2, 1.7, 1.0, [BasicAttack("Chalice of the wicked",.6),Corruption("Corruption", 0.2), HolyLight("Holy Light", 0.10), DivineShield("Divine Shield", 0.1)]),
    ]

    def __init__(
        self,
        name: str,
        max_health: int,
        damage: int,
        spell_power: int,
        image_path: str,
        symbol: str = "",
        health: int = None,
        size: int = 100,
        shake: int = 0,
        selected: bool = False,
        is_boss: bool = False,
        monster_type: MonsterType = None,
        shields: int = 0,
        level: int = 1,
    ):
        self.name = name
        self.max_health = max_health
        self.health = max_health  # Always start with max health
        self.damage = damage
        self.spell_power = spell_power
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
        self.intention: str = ""
        self.intention_icon_types: List[IconType] = []
        
        self.power_rating = self.calculate_power_rating()

    def calculate_power_rating(self):
        base_survivability = self.max_health / 6  # Assuming the player deals ~6 damage per round
        ability_power = sum(self.calculate_ability_power(ability) for ability in self.monster_type.abilities) if self.monster_type else 0
        return base_survivability * ability_power

    def calculate_ability_power(self, ability):
        # Calculate the power contribution without applying effects
        power_contribution = ability.calculate_power_contribution(self)
        return power_contribution * ability.probability

    def __str__(self):
        return f"{self.name} (HP: {self.health}/{self.max_health}, DMG: {self.damage}, SP: {self.spell_power})"

    def attack(self, player):
        total_damage = self.damage
        player.take_damage(total_damage)

    def defend(self):
        shield_amount = round(self.spell_power * 0.5)
        self.grant_shields(shield_amount)
        return f"{self.name} defends, gaining {shield_amount} shields!"

    def buff(self):
        buff_amount = round(self.spell_power * 0.2)
        return f"{self.name} buffs, gaining {buff_amount} Strength for 2 turns!"

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
        self.health = max(0, self.health - damage)
        actual_damage = old_health - self.health
        health_percentage = (actual_damage / self.max_health) * 100
        self.shake += round(min(health_percentage, 100))
        return actual_damage

    def is_alive(self) -> bool:
        return self.health > 0

    def grant_shields(self, amount: int):
        self.shields += amount

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def take_damage(self, damage: int) -> int:
        return self.receive_damage(damage)

    def apply_status_effects(self):
        self.status_effects.apply_effects(self)

    def execute_action(self, action: str, target):
        if self.monster_type and self.monster_type.abilities:
            ability = next((a for a in self.monster_type.abilities if a.name == action), None)
            if ability:
                return ability.use(self, target)

        print(f"WARNING: no matching ability found for {action}")
        return f"{self.name} does nothing."

    def decide_action(self, player) -> str:
        if self.monster_type and self.monster_type.abilities:
            chosen_ability = random.choices(
                self.monster_type.abilities,
                weights=[ability.probability for ability in self.monster_type.abilities],
                k=1
            )[0]
            self.intention = chosen_ability.name
            self.intention_icon_types = chosen_ability.icon_types
        else:
            print(f"WARNING: {self.name} has no abilities")
            self.intention_icon_types = [IconType.UNKNOWN]
        return self.intention

    @staticmethod
    def generate(level: int, is_boss: bool = False):
        if is_boss:
            monster_type = random.choice(Monster.boss_types)
        else:
            monster_type = random.choices(
                Monster.monster_types,
                weights=[1 / mt.rarity for mt in Monster.monster_types],
                k=1
            )[0]

        base_health = 12 + math.log(level + 1, 3) * 8
        base_damage = 6 + math.log(level + 1, 3) * 3
        base_spell_power = 6 + math.log(level + 1, 3) * 3

        health = round(base_health * monster_type.health_mult * random.uniform(0.9, 1.1))
        damage = round(base_damage * monster_type.damage_mult * random.uniform(0.9, 1.1))
        spell_power = round(base_spell_power * monster_type.spell_power_mult * random.uniform(0.9, 1.1))

        name = f"{monster_type.name} L{level}"
        image_path = f"./assets/images/characters/{monster_type.name.lower().replace(' ', '_')}.png"

        return Monster(name, health, damage, spell_power, image_path, monster_type.symbol, 
                       monster_type=monster_type, is_boss=is_boss, level=level)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "damage": self.damage,
            "spell_power": self.spell_power,
            "image_path": self.image_path,
            "symbol": self.symbol,
            "shields": self.shields,
            "shake": self.shake,
            "selected": self.selected,
            "is_boss": self.is_boss,
            "status_effects": self.status_effects.to_dict(),
            "monster_type": self.monster_type.name if self.monster_type else None,
            "level": self.level,
            "power_rating": self.power_rating,
            "intention": self.intention
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Monster':
        monster_type = next((mt for mt in cls.monster_types + cls.boss_types if mt.name == data["monster_type"]), None)
        monster = cls(
            data["name"],
            data["max_health"],
            data["damage"],
            data["spell_power"],
            data["image_path"],
            data["symbol"],
            health=data["max_health"],  # Always start with max health
            shields=data["shields"],
            shake=data["shake"],
            selected=data["selected"],
            is_boss=data["is_boss"],
            monster_type=monster_type,
            level=data["level"]
        )
        monster.status_effects = StatusEffectManager.from_dict(data["status_effects"])
        monster.power_rating = data["power_rating"]
        monster.intention = data.get("intention", "")
        return monster