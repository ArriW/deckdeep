from abc import ABC, abstractmethod
from typing import List, Dict
from deckdeep.status_effect import StatusEffectManager, Bleed, HealthRegain
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

    def calculate_power_rating(self):
        base_power = (self.max_health * self.damage * self.spell_power) ** (1 / 3)
        if self.monster_type and hasattr(self.monster_type, 'abilities'):
            ability_power = sum(
                ability.power_contribution for ability in self.monster_type.abilities
            )
        else:
            ability_power = 0
        return base_power * (1 + ability_power / 100) 



    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> Dict:
        data = {
            key: value for key, value in vars(self).items() if not key.startswith("_")
        }
        data["status_effects"] = self.status_effects.to_dict()
        data["monster_type"] = self.monster_type.name if self.monster_type else None
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Monster":
        status_effects = data.pop("status_effects", {})
        monster_type_name = data.pop("monster_type", None)
        
        # Create the monster instance without calculating power_rating
        monster = cls(**data)
        
        monster.status_effects = StatusEffectManager.from_dict(status_effects)
        
        if monster_type_name:
            monster.monster_type = next(
                (
                    mt
                    for mt in cls.monster_types + cls.boss_types
                    if mt.name == monster_type_name
                ),
                None,
            )
        
        # Calculate power_rating after monster_type is set
        if monster.monster_type:
            monster.power_rating = monster.calculate_power_rating()
        else:
            # Set a default power_rating or calculate it differently if monster_type is None
            monster.power_rating = (monster.max_health * monster.damage * monster.spell_power) ** (1/3)
        
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

    def decide_action(self, target) -> str:
        if self.monster_type and self.monster_type.abilities:
            for ability in self.monster_type.abilities:
                if random.random() < ability.probability:
                    return ability.use(self, target)

        # Default action: attack
        damage = self.damage
        target.take_damage(damage)
        return f"{self.name} attacks for {damage} damage."


    @classmethod
    def generate(cls, level: int) -> "Monster":
        weights = [mt.rarity for mt in cls.monster_types]
        monster_type = random.choices(cls.monster_types, weights=weights)[0]
        base_health = round(15 + level * 3)
        base_damage = round(4 + level * 1.1)
        base_spell_power = round(3 + level * 1.2)
        max_health = round(base_health * monster_type.health_mult)
        damage = round(base_damage * monster_type.damage_mult)
        spell_power = round(base_spell_power * monster_type.spell_power_mult)
        image_path = f"./assets/images/characters/{monster_type.name.lower()}.png"
        monster = cls(
            name=monster_type.name,
            max_health=max_health,
            damage=damage,
            spell_power=spell_power,
            image_path=image_path,
            symbol=monster_type.symbol,
            monster_type=monster_type,
            level=level,
        )
        return monster

    @classmethod
    def generate_boss(cls, level: int) -> "Monster":
        boss_type = random.choice(cls.boss_types)
        base_health = round(30 + level * 5)
        base_damage = round(8 + level * 1.6)
        base_spell_power = round(6 + level * 1.5)
        max_health = round(base_health * boss_type.health_mult)
        damage = round(base_damage * boss_type.damage_mult)
        spell_power = round(base_spell_power * boss_type.spell_power_mult)
        image_path = f"./assets/images/characters/{boss_type.name.lower()}.png"
        monster = cls(
            name=f"Boss {boss_type.name}",
            max_health=max_health,
            damage=damage,
            spell_power=spell_power,
            image_path=image_path,
            symbol=boss_type.symbol,
            is_boss=True,
            size=300, 
            monster_type=boss_type,
            level=level,
        )
        return monster

