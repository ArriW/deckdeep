from abc import ABC, abstractmethod
from typing import List, Dict
from deckdeep.status_effect import StatusEffectManager, Bleed, HealthRegain
import random
from typing import Dict, Optional
from deckdeep.status_effect import StatusEffectManager, Bleed
from deckdeep.config import scale
import random
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


class SneakAttack(Ability):
    def use(self, user, target):
        damage = round(user.damage * 1.5)
        self._power_contribution = damage
        target.take_damage(damage)
        return f"{user.name} performs a Sneak Attack for {damage} damage!"

class InfectiousBite(Ability):
    def use(self, user, target):
        bleed_damage = round(user.damage*0.25)
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
        damage = round(user.spell_power)
        self._power_contribution = damage * 0.5 * self.probability 
        bleed = Bleed(damage*.1)
        target.take_damage(damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} breathes fire for {damage} damage and inflicts {damage} Bleed!"

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

# Update MonsterType to use the new Ability classes
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
        MonsterType("Goblin", "G", 0.7, 0.9, 0.6, 1.0, [SneakAttack("Sneak Attack", 0.5)]),
        MonsterType("Zombie_1", "Z1", 0.4, 1.1, 0.5, 1.0, [InfectiousBite("Infectious Bite", 0.7)]),
        MonsterType("Orc_1", "O1", 1.0, 1.0, 0.7, 0.8, [Rage("Rage", 0.4), BattleCry("Battle Cry", 0.3)]),
        MonsterType("Orc_2", "O2", 1.0, 0.6, 0.7, 1.0, [BattleCry("Battle Cry", 0.3), ShieldUp("Shield Up", 0.35)]),
        MonsterType("Zombie_2", "Z2", 1.1, 0.5, 0.6, 1.0, [Regenerate("Regenerate", 0.35)]),
        MonsterType("Troll", "T", 1.3, 1.1, 0.8, 0.6, [Regenerate("Regenerate", 0.45)]),
        MonsterType("Guardian_1", "G1", 1.3, 0.5, 0.7, 0.7, [Fortify("Fortify", 0.4), PowerOverTime("Power over time", 0.4)]),
        MonsterType("Guardian_2", "G2", 0.7, 0.9, 0.8, 0.7, [ShieldUp("Protect", 0.35), PowerOverTime("Power over time", 0.4), Regenerate("Mend", 0.25)]),
        MonsterType("Witch", "W", 0.7, 0.6, 1.2, 0.7, [Curse("Curse", 0.5), MagicMissile("Magic Missile", 0.4)]),
    ]

    boss_types: List[MonsterType] = [
        MonsterType("Troll", "TB", 1.6, 0.7, 1.0, 1.0, [TrollRegeneration("Troll Regeneration", 0.35)]),
        MonsterType("Dragon", "D", 1.4, 1.2, 1.3, 1.0, [FireBreath("Fire Breath", 0.20)]),
        MonsterType("Corrupted_Paladin", "CP", 1.1, 1.1, 1.2, 1.0, [Corruption("Corruption", 0.3), HolyLight("Holy Light", 0.25), DivineShield("Divine Shield", 0.3)]),
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
        power_rating: int = 0,
    ):
        self.name = name
        self.health = health
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
            ability_power = sum(
                ability.power_contribution for ability in self.monster_type.abilities
            )
        else:
            ability_power = 0
        return base_power * (1 + ability_power / 100) 


    def __str__(self):
        return f"{self.name} (HP: {self.health}/{self.max_health}, DMG: {self.damage})"

    def attack(self, player):
        total_damage = self.damage  
        player.take_damage(total_damage)

    def defend(self):
        shield_amount = round(self.spell_power * 0.5)
        self.grant_shields(shield_amount)
        return f"{self.name} defends, gaining {shield_amount} shields!"

    def buff(self):
        buff_amount = round(self.spell_power * 0.2)
        # put buff here
        return f"{self.name} buffs, gaining {buff_amount} Strength!"

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

    def is_alive(self) -> bool:
        return self.health > 0

    def grant_shields(self, amount: int):
        self.shields += amount

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def add_shields(self, amount: int):
        self.shields += amount

    def take_damage(self, damage: int) -> int:
        return self.receive_damage(damage)


    def apply_status_effects(self):
        self.status_effects.apply_effects(self)

    def execute_action(self, action: str, target):
        if self.monster_type and self.monster_type.abilities:
            ability = next((a for a in self.monster_type.abilities if a.name == action), None)
            if ability:
                return ability.use(self, target)

        # Fallback to basic actions if no matching ability is found
        if action == "attack":
            return self.attack(target)
        elif action == "defend":
            return self.defend()
        elif action == "buff":
            return self.buff()
        else:
            return f"{self.name} does nothing."

    def decide_action(self, player) -> str:
        # Simple AI: 70% chance to attack, 20% chance to defend, 10% chance to buff
        action_roll = random.random()
        if action_roll < 0.7:
            self.intention = "attack"
        elif action_roll < 0.9:
            self.intention = "defend"
        else:
            self.intention = "buff"
        return self.intention

    @staticmethod
    def generate(level: int):
        name = f"Monster L{level}"
        health = random.randint(level * 10, level * 15)
        damage = random.randint(level * 2, level * 3)
        image_path = "./assets/images/characters/Orc_1.png"
        return Monster(name, health, health, damage, image_path)

    @staticmethod
    def generate_boss(level: int):
        name = f"Boss L{level}"
        health = random.randint(level * 20, level * 30)
        damage = random.randint(level * 4, level * 6)
        image_path = "./assets/images/characters/boss.png"
        return Monster(name, health, health, damage, image_path)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "damage": self.damage,
            "image_path": self.image_path,
            "shields": self.shields,
            "shake": self.shake,
            "selected": self.selected,
            "status_effects": self.status_effects.to_dict(),
            "power_rating": self.power_rating,
            "intention": self.intention
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Monster':
        monster = cls(
            
            data["name"],
            data["health"],
            data["max_health"],
            data["damage"],
            data["image_path"]
        )
        monster.shields = data["shields"]
        monster.shake = data["shake"]
        monster.selected = data["selected"]
        monster.status_effects = StatusEffectManager.from_dict(data["status_effects"])
        monster.power_rating = data["power_rating"]
        monster.intention = data.get("intention", "")  # Use get() to handle cases where intention might not be in the saved data
        return monster

