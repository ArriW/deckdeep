from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import random
import math
from deckdeep.status_effect import StatusEffectManager, Bleed, HealthRegain
from deckdeep.config import scale

class Ability(ABC):
    def __init__(self, name: str, probability: float):
        self.name = name
        self.probability = probability
        self._power_contribution = 0

    @abstractmethod
    def use(self, user, target):
        pass

    @property
    def power_contribution(self):
        return self._power_contribution

# Existing abilities
class SneakAttack(Ability):
    def use(self, user, target):
        damage = round(user.damage * 1.5)
        self._power_contribution = damage
        target.take_damage(damage)
        return f"{user.name} performs a Sneak Attack for {damage} damage!"

class InfectiousBite(Ability):
    def use(self, user, target):
        bleed_damage = round(user.damage * 0.25)
        self._power_contribution = bleed_damage
        bleed = Bleed(bleed_damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} inflicts an Infectious Bite, causing {bleed_damage} Bleed!"

class Rage(Ability):
    def use(self, user, target):
        old_damage = user.damage
        user.damage = round(user.damage * 1.2)
        self._power_contribution = user.damage - old_damage
        return f"{user.name} enters a Rage, increasing damage from {old_damage} to {user.damage}!"

class BattleCry(Ability):
    def use(self, user, target):
        heal_amount = round(user.spell_power * 0.5)
        self._power_contribution = heal_amount
        user.heal(heal_amount)
        return f"{user.name} uses Battle Cry, healing for {heal_amount}!"

class ShieldUp(Ability):
    def use(self, user, target):
        shield_amount = round(user.max_health * 0.3)
        self._power_contribution = shield_amount
        user.grant_shields(shield_amount)
        return f"{user.name} uses Shield Up, gaining {shield_amount} shields!"

class Regenerate(Ability):
    def use(self, user, target):
        heal_amount = round(user.max_health * 0.2)
        self._power_contribution = heal_amount
        user.heal(heal_amount)
        return f"{user.name} Regenerates, healing for {heal_amount}!"

class Fortify(Ability):
    def use(self, user, target):
        shield_amount = round(user.max_health * 0.4)
        self._power_contribution = shield_amount
        user.grant_shields(shield_amount)
        return f"{user.name} Fortifies, gaining {shield_amount} shields!"

class PowerOverTime(Ability):
    def use(self, user, target):
        old_damage = user.damage
        user.damage = round(user.damage * 1.2)
        damage_dealt = round(user.damage)
        self._power_contribution = (user.damage - old_damage) + damage_dealt
        target.take_damage(damage_dealt)
        return f"{user.name}'s power increases from {old_damage} to {user.damage} and deals {damage_dealt} damage!"

class Curse(Ability):
    def use(self, user, target):
        bleed_damage = round(user.spell_power * 0.3)
        self._power_contribution = bleed_damage
        bleed = Bleed(bleed_damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} Curses the target, causing {bleed_damage} Bleed!"

class MagicMissile(Ability):
    def use(self, user, target):
        damage = round(user.spell_power)
        self._power_contribution = damage
        target.take_damage(damage)
        return f"{user.name} casts Magic Missile for {damage} damage!"

class TrollRegeneration(Ability):
    def use(self, user, target):
        heal_amount = round(user.max_health * 0.1)
        regen_amount = round(user.spell_power)
        self._power_contribution = heal_amount + regen_amount
        user.heal(heal_amount)
        regen = HealthRegain(regen_amount)
        user.status_effects.add_effect(regen)
        return f"{user.name} uses Troll Regeneration, healing for {heal_amount} and gaining {regen_amount} Health Regeneration!"

class FireBreath(Ability):
    def use(self, user, target):
        damage = round(user.spell_power * 1.5)
        self._power_contribution = damage * 0.5 * self.probability 
        bleed = Bleed(v:=round(damage * 0.1))
        target.take_damage(damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} breathes fire for {damage} damage and inflicts {v} Bleed!"

class Corruption(Ability):
    def use(self, user, target):
        bleed_damage = round(user.spell_power * 0.3)
        self._power_contribution = bleed_damage
        bleed = Bleed(bleed_damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} corrupts the target, causing {bleed_damage} Bleed!"

class HolyLight(Ability):
    def use(self, user, target):
        heal_amount = round(user.max_health * 0.3)
        self._power_contribution = heal_amount
        user.heal(heal_amount)
        return f"{user.name} uses Holy Light, healing for {heal_amount}!"

class DivineShield(Ability):
    def use(self, user, target):
        shield_amount = round(user.max_health * 0.4)
        self._power_contribution = shield_amount
        user.grant_shields(shield_amount)
        return f"{user.name} gains a Divine Shield of {shield_amount}!"

# New abilities
class PoisonDart(Ability):
    def use(self, user, target):
        damage = round(user.spell_power * 0.5)
        # weakness = Weakness(2, 2)  # 2 turns of -2 damage
        self._power_contribution = damage + 4  # Estimating the value of weakness
        target.take_damage(damage)
        # target.status_effects.add_effect(weakness)
        return f"{user.name} fires a Poison Dart for {damage} damage and applies Weakness!"

class ThunderClap(Ability):
    def use(self, user, target):
        damage = round(user.damage * 0.8)
        # vulnerable = Vulnerable(2, 1.5)  # 2 turns of 50% increased damage taken
        self._power_contribution = damage * 1.25  # Estimating the value of vulnerable
        target.take_damage(damage)
        # target.status_effects.add_effect(vulnerable)
        return f"{user.name} uses Thunder Clap for {damage} damage and applies Vulnerable!"

class LifeDrain(Ability):
    def use(self, user, target):
        damage = round(user.spell_power * 0.7)
        heal = round(damage * 0.5)
        self._power_contribution = damage + heal
        target.take_damage(damage)
        user.heal(heal)
        return f"{user.name} uses Life Drain, dealing {damage} damage and healing for {heal}!"

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
        MonsterType("Zombie_1", "Z", 1.0, 0.8, 0.5, 1.0, [InfectiousBite("Infectious Bite", 0.7)]),
        MonsterType("Zombie_2", "Z", 1.0, 0.8, 0.5, 1.0, [InfectiousBite("Infectious Bite", 0.7)]),
        MonsterType("Orc_1", "O", 1.1, 1.1, 0.7, 0.8, [Rage("Rage", 0.4), BattleCry("Battle Cry", 0.3), ThunderClap("Thunder Clap", 0.3)]),
        MonsterType("Orc_2", "O", 1.1, 1.1, 0.7, 0.8, [Rage("Rage", 0.4), BattleCry("Battle Cry", 0.3), ThunderClap("Thunder Clap", 0.3)]),
        MonsterType("Troll", "T", 1.3, 1.1, 0.8, 0.6, [Regenerate("Regenerate", 0.45), PowerOverTime("Power over time", 0.35)]),
        MonsterType("Witch", "W", 0.7, 0.6, 1.2, 0.7, [Curse("Curse", 0.5), MagicMissile("Magic Missile", 0.4), LifeDrain("Life Drain", 0.3)]),
        MonsterType("Guardian_1", "GL", 1.5, 0.7, 0.5, 0.5, [Fortify("Fortify", 0.6), ShieldUp("Shield Up", 0.4)]),
        MonsterType("Guardian_2", "D", 0.9, 1.2, 1.0, 0.4, [FireBreath("Fire Breath", 0.3), Corruption("Corruption", 0.4), LifeDrain("Life Drain", 0.3)]),
    ]

    boss_types: List[MonsterType] = [
        MonsterType("Troll", "TK", 1.8, 1.2, 1.0, 1.0, [TrollRegeneration("Troll Regeneration", 0.4), ThunderClap("Thunder Clap", 0.3), PowerOverTime("Power over time", 0.3)]),
        MonsterType("Dragon", "DR", 1.6, 1.4, 1.3, 1.0, [FireBreath("Fire Breath", 0.25), Fortify("Fortify", 0.2), PowerOverTime("Power over time", 0.2)]),
        MonsterType("Corrupted Paladin", "CP", 1.4, 1.1, 1.2, 1.0, [Corruption("Corruption", 0.3), HolyLight("Holy Light", 0.25), DivineShield("Divine Shield", 0.3)]),
        # MonsterType("Necromancer", "NC", 1.2, 0.9, 1.6, 1.0, [Curse("Curse", 0.3), LifeDrain("Life Drain", 0.3), MagicMissile("Magic Missile", 0.2), Corruption("Corruption", 0.2)]),
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
        self.health = health if health is not None else max_health
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
        self.power_rating = self.calculate_power_rating()
        self.intention: str = ""

    def calculate_power_rating(self):
        base_power = (self.max_health * self.damage * self.spell_power) ** (1 / 3)
        if self.monster_type and hasattr(self.monster_type, 'abilities'):
            ability_power = sum(ability.power_contribution for ability in self.monster_type.abilities)
        else:
            ability_power = 0
        return base_power * (1 + ability_power / 100)

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
        # strength = Strength(2, buff_amount)  # 2 turns of increased damage
        # self.status_effects.add_effect(strength)
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
        self.shake = round(min(health_percentage, 100))
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

        # Fallback to basic actions if no matching ability is foundi
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
        else:
            print(f"WARNING: {self.name} has no abilities")
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

        base_health = level * 10
        base_damage = level * 2
        base_spell_power = level * 1.5

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
            health=data["health"],
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