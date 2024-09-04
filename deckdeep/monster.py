
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
import random
import math
from abc import ABC, abstractmethod
from deckdeep.status_effect import StatusEffectManager, Bleed, HealthRegain, Weakness, Bolster, Burn
from deckdeep.config import scale

from enum import Enum


if TYPE_CHECKING:
    from deckdeep.player import Player
    from deckdeep.monster_group import MonsterGroup
    from deckdeep.monster import Monster


class IconType(Enum):
    ATTACK = 1
    DEFEND = 2
    BUFF = 3
    BLEED = 4
    HEAL = 5
    MAGIC = 6
    UNKNOWN = 7


class Ability(ABC):
    def __init__(self, name: str, probability: float, icon_types: List[IconType], num_attacks: int = 1):
        self.name = name
        self.probability = probability
        self._power_contribution = 0
        self.icon_types = icon_types
        self.num_attacks = num_attacks

    @abstractmethod
    def use(self,user: "Monster",target: "Player") -> str:
        pass

    @abstractmethod
    def calculate_power_contribution(self, user: "Monster") -> int:
        pass

    @property
    def power_contribution(self):
        return self._power_contribution

    @power_contribution.setter
    def power_contribution(self, value):
        self._power_contribution = value

    def apply_weakness(self, user: "Monster", damage: int) -> int:
        weakness_effect = next((effect for effect in user.status_effects.effects if isinstance(effect, Weakness)), None)
        if weakness_effect:
            return max(0, damage - weakness_effect.value)
        return damage


class BasicAttack(Ability):
    def __init__(self, name: str, probability: float, num_attacks: int = 1):
        super().__init__(name, probability, [IconType.ATTACK] * num_attacks, num_attacks)

    def use(self,user: "Monster",target: "Player") -> str:
        total_damage = 0
        for _ in range(self.num_attacks):
            damage = self.apply_weakness(user, user.damage)
            target.take_damage(damage)
            total_damage += damage
        return f"{user.name} attacks {self.num_attacks} times for a total of {total_damage} damage!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return user.damage * self.num_attacks


class SneakAttack(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK])

    def use(self,user: "Monster",target: "Player") -> str:
        damage = self.apply_weakness(user, round(user.damage * 1.5))
        target.take_damage(damage)
        return f"{user.name} performs a Sneak Attack for {damage} damage!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.damage * 1.5)


class InfectiousBite(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.BLEED])

    def use(self,user: "Monster",target: "Player") -> str:
        damage = self.apply_weakness(user, round(user.damage * 0.25))
        target.take_damage(damage)
        bleed_damage = max(damage, 1)
        bleed = Bleed(bleed_damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} inflicts an Infectious Bite, causing {bleed_damage} Bleed!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return max(round(user.damage * 0.25), 1)


class Rage(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.BUFF])

    def use(self,user: "Monster",target: "Player") -> str:
        old_damage = user.damage
        user.damage = round(user.damage * 1.2)
        return f"{user.name} enters a Rage, increasing damage from {old_damage} to {user.damage}!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.damage * 0.2)


class BattleCry(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.HEAL])

    def use(self,user: "Monster",target: "Player") -> str:
        heal_amount = round(user.spell_power * 0.5)
        user.heal(heal_amount)
        return f"{user.name} uses Battle Cry, healing for {heal_amount}!"

    def calculate_power_contribution(self, user):
        return round(user.spell_power * 0.5)


class ShieldUp(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.DEFEND])

    def use(self,user: "Monster",target: "Player") -> str:
        shield_amount = round(user.max_health * 0.3)
        user.grant_shields(shield_amount)
        return f"{user.name} uses Shield Up, gaining {shield_amount} shields!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.max_health * 0.3)


class Regenerate(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.HEAL])

    def use(self,user: "Monster",target: "Player") -> str:
        heal_amount = round(user.max_health * 0.25)
        user.heal(heal_amount)
        return f"{user.name} Regenerates, healing for {heal_amount}!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.max_health * 0.25)


class Fortify(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.DEFEND])

    def use(self,user: "Monster",target: "Player") -> str:
        shield_amount = round(user.max_health * 0.2)
        user.grant_shields(shield_amount)
        return f"{user.name} Fortifies, gaining {shield_amount} shields!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.max_health * 0.2)


class PowerOverTime(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.BUFF])

    def use(self,user: "Monster",target: "Player") -> str:
        old_damage = user.damage
        damage_dealt = self.apply_weakness(user, round(user.damage))
        user.damage = round(user.damage * 1.2)
        target.take_damage(damage_dealt)
        return f"{user.name}'s power increases from {old_damage} to {user.damage} and deals {damage_dealt} damage!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.damage * 0.2) + user.damage


class Curse(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.MAGIC, IconType.BLEED])

    def use(self,user: "Monster",target: "Player") -> str:
        bleed_damage = max(round(user.spell_power * 0.2),1)
        bleed = Bleed(bleed_damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} Curses the target, causing {bleed_damage} Bleed!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return max(round(user.spell_power * 0.2),1)


class MagicMissile(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.HEAL])

    def use(self,user: "Monster",target: "Player") -> str:
        user.heal(round(user.spell_power * 0.4))
        damage = self.apply_weakness(user, round(user.spell_power))
        target.take_damage(damage)
        return f"{user.name} casts Magic Missile for {damage} damage!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.spell_power+round(user.spell_power * 0.4))


class TrollRegeneration(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.HEAL, IconType.BUFF])

    def use(self,user: "Monster",target: "Player") -> str:
        heal_amount = round(user.max_health * 0.1)
        regen_amount = round(user.spell_power * 0.3)
        user.heal(heal_amount)
        regen = HealthRegain(regen_amount)
        user.status_effects.add_effect(regen)
        return f"{user.name} uses Troll Regeneration, healing for {heal_amount} and gaining {regen_amount} Health Regeneration!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.max_health * 0.1) + round(user.spell_power * 0.3)


class FireBreath(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.BLEED])

    def use(self,user: "Monster",target: "Player") -> str:
        damage = self.apply_weakness(user, round(user.spell_power * 1.5))
        bleed = Bleed(v := round(damage * 0.1))
        target.take_damage(damage)
        target.status_effects.add_effect(bleed)
        return f"{user.name} breathes fire for {damage} damage and inflicts {v} Bleed!"

    def calculate_power_contribution(self, user):
        damage = round(user.spell_power * 1.5)
        return damage + round(damage * 0.1)


class Corruption(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.BLEED])

    def use(self,user: "Monster",target: "Player") -> str:
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

    def use(self,user: "Monster",target: "Player") -> str:
        heal_amount = round(user.max_health * 0.3)
        user.heal(heal_amount)
        return f"{user.name} uses Holy Light, healing for {heal_amount}!"

    def calculate_power_contribution(self, user):
        return round(user.max_health * 0.3)


class DivineShield(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.DEFEND])

    def use(self,user: "Monster",target: "Player") -> str:
        shield_amount = round(user.max_health * 0.4)
        user.grant_shields(shield_amount)
        return f"{user.name} gains a Divine Shield of {shield_amount}!"

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.max_health * 0.4)


class PoisonDart(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.BLEED])

    def use(self,user: "Monster",target: "Player") -> str:
        damage = self.apply_weakness(user, round(user.spell_power * 0.5))
        target.take_damage(damage)
        return (
            f"{user.name} fires a Poison Dart for {damage} damage!"
        )

    def calculate_power_contribution(self, user: "Monster") -> int:
        return round(user.spell_power * 0.5)


class ThunderClap(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.BUFF])

    def use(self,user: "Monster",target: "Player") -> str:
        damage = self.apply_weakness(user, round(user.damage * 0.8))
        target.take_damage(damage)
        weakness = Weakness(1)
        target.status_effects.add_effect(weakness)
        return f"{user.name} uses Thunder Clap for {damage} damage and applies 1 Weakness!"

    def calculate_power_contribution(self, user):
        return round(user.damage * 0.8 * 1.25)  # Estimating the value of Weakness


class LifeDrain(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.ATTACK, IconType.HEAL])

    def use(self,user: "Monster",target: "Player") -> str:
        damage = self.apply_weakness(user, round(user.spell_power * 0.7))
        heal = round(damage * 0.5)
        target.take_damage(damage)
        user.heal(heal)
        return f"{user.name} uses Life Drain, dealing {damage} damage and healing for {heal}!"

    def calculate_power_contribution(self, user):
        damage = round(user.spell_power * 0.7)
        return damage + round(damage * 0.5)

class Enfeeblement(Ability):
    def __init__(self, name: str, probability: float):
        super().__init__(name, probability, [IconType.MAGIC])
        
    def use(self,user: "Monster",target: "Player") -> str:
        target.status_effects.add_effect(Weakness(v:=max(1,user.spell_power//5)))
        return f"{user.name} Enfeebles the target, causing {v} Weakness!"

    def calculate_power_contribution(self, user):
        return max(1,user.spell_power//5)*3


class MonsterType:
    def __init__(
        self,
        name: str,
        symbol: str,
        health_mult: float,
        damage_mult: float,
        spell_power_mult: float,
        rarity: float,
        abilities: Optional[List[Ability]] = None,
        monster_level_limits: Optional[Tuple] = None
    ):
        self.name = name
        self.symbol = symbol
        self.health_mult = health_mult
        self.damage_mult = damage_mult
        self.spell_power_mult = spell_power_mult
        self.rarity = rarity
        self.abilities = abilities or []
        self.monster_level_limits = monster_level_limits 


class Monster:
    monster_types: List[MonsterType] = [
        MonsterType(
            "goblin_1",
            "G",
            0.7,
            0.9,
            0.6,
            1.0,
            [SneakAttack("Sneak Attack", 0.5), PoisonDart("Poison Dart", 0.3)],
        ),
        MonsterType(
            "Zombie_1",
            "Z",
            0.8,
            1.0,
            0.3,
            1.0,
            [InfectiousBite("Infectious Bite", 0.7), BasicAttack("Claw", 0.3)],
        ),
        MonsterType(
            "Zombie_2",
            "Z",
            0.8,
            1.0,
            0.3,
            1.0,
            [InfectiousBite("Infectious Bite", 0.7), BasicAttack("Claw", 0.3)],
        ),
        MonsterType(
            "Zombie_3",
            "Z",
            0.3,
            1.3,
            0.3,
            1.0,
            [InfectiousBite("Infectious Bite", 0.7), BasicAttack("Claw", 0.3)],
        ),
        MonsterType(
            "Orc_1",
            "O",
            0.9,
            1.1,
            0.7,
            0.8,
            [Rage("Rage", 0.4), BasicAttack("Axe Attack", 0.6)],
        ),
        MonsterType(
            "Orc_2",
            "O",
            1.1,
            0.9,
            0.7,
            0.8,
            [
                BattleCry("Battle Cry", 0.3),
                ShieldUp("Block", 0.2),
                BasicAttack("Axe Attack", 0.5),
            ],
        ),
        MonsterType(
            "troll_1",
            "T",
            1.3,
            1.1,
            0.8,
            0.6,
            [Regenerate("Regenerate", 0.35), BasicAttack("Fist", 0.65)],
        ),
        MonsterType(
            "witch_1",
            "W",
            .8,
            1.0,
            1.2,
            0.7,
            [
                Curse("Curse", 0.5),
                MagicMissile("Magic Missile", 0.4),
                LifeDrain("Life Drain", 0.3),
                BasicAttack("Staff Attack", 0.3),
            ],
        ),
        MonsterType(
            "Guardian_1",
            "GL",
            1.5,
            0.8,
            0.5,
            0.5,
            [
                BasicAttack("Sword Attack", 0.6),
                ShieldUp("Shield Up", 0.3),
                PowerOverTime("Power over time", 0.1),
            ],
        ),
        MonsterType(
            "Guardian_2",
            "D",
            1.5,
            1.2,
            1.0,
            0.4,
            [
                FireBreath("Fire Breath", 0.3),
                Corruption("Corruption", 0.4),
                LifeDrain("Life Drain", 0.3),
            ],
        ),
    ]

    boss_types: List[MonsterType] = [
        MonsterType(
            "troll_king",
            "TK",
            4.4,
            1.5,
            1.0,
            1.0,
            [
                TrollRegeneration("Troll Regeneration", 0.25),
                PowerOverTime("Power over time", 0.2),
                BasicAttack("Sword Attack", 0.55),
            ],
        ),
        MonsterType(
            "dragon_1",
            "DR",
            2.8,
            2.2,
            1.3,
            1.0,
            [
                FireBreath("Fire Breath", 0.25),
                Fortify("Fortify", 0.2),
                BasicAttack("Claw Attack", 0.35),
            ],
        ),
        MonsterType(
            "corrupted_paladin",
            "CP",
            2.5,
            2.0,
            2.0,
            1.0,
            [
                BasicAttack("Chalice of the wicked", 0.5),
                Corruption("Corruption", 0.2),
                HolyLight("Holy Light", 0.10),
                DivineShield("Divine Shield", 0.2),
            ],
        ),
    ]

    def __init__(
        self,
        name: str,
        max_health: int,
        damage: int,
        spell_power: int,
        image_path: str,
        symbol: str = "",
        health: Optional[int] = None,
        size: int = 100,
        shake: int = 0,
        selected: bool = False,
        is_boss: bool = False,
        monster_type: Optional['MonsterType'] = None,
        shields: int = 0,
        level: int = 1,
    ):
        self.name: str = name
        self.max_health: int = max_health
        self.health: int = health if health is not None else max_health
        self.damage: int = damage
        self.spell_power: int = spell_power
        self.image_path: str = image_path
        self.symbol: str = symbol
        self.size: int = scale(size)
        self.shake: int = shake
        self.selected: bool = selected
        self.is_boss: bool = is_boss
        self.status_effects: StatusEffectManager = StatusEffectManager()
        self.monster_type: Optional['MonsterType'] = monster_type
        self.shields: int = shields
        self.level: int = level
        self.intention: Optional[Ability] = None
        self.intention_icon_types: List[IconType] = []

        self.power_rating: float = self.calculate_power_rating()

        self.is_dying = False
        self.death_start_time = 0

    def calculate_power_rating(self):
        base_survivability = (
            self.max_health / 6
        )  # Assuming the player deals ~6 damage per round
        ability_power = (
            sum(
                self.calculate_ability_power(ability)
                for ability in self.monster_type.abilities
            )
            if self.monster_type
            else 0
        )
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

    def take_damage(self, damage: int):
        # Apply Bolster effect
        bolster_effect = next((effect for effect in self.status_effects.effects if isinstance(effect, Bolster)), None)
        if bolster_effect:
            damage = max(0, damage - bolster_effect.value)

        # Handle shield absorption
        if self.shields > 0:
            if damage <= self.shields:
                self.shields -= damage
                damage = 0
            else:
                damage -= self.shields
                self.shields = 0

        # Apply remaining damage to health
        self.health = max(0, self.health - damage)

    def deal_damage(self, base_damage: int, num_attacks: int = 1) -> int:
        total_damage = 0
        for _ in range(num_attacks):
            # Apply Weakness effect
            weakness_effect = next((effect for effect in self.status_effects.effects if isinstance(effect, Weakness)), None)
            if weakness_effect:
                damage = max(0, base_damage - weakness_effect.value)
            else:
                damage = base_damage
            total_damage += damage
        return total_damage

    def apply_status_effects(self):
        self.status_effects.apply_effects(self)

    def execute_action(self, target):
        if self.intention:
            print(f"DEBUG: Executing ability {self.intention.__class__.__name__} for {self.name}")
            return self.intention.use(self, target)
        else:
            print(f"WARNING: No intention set for {self.name}")
            return f"{self.name} does nothing."

    def decide_action(self, player) -> str:
        if self.monster_type and self.monster_type.abilities:
            self.intention = random.choices(
                self.monster_type.abilities,
                weights=[ability.probability for ability in self.monster_type.abilities],
                k=1
            )[0]
            self.intention_icon_types = self.intention.icon_types
            print(f"DEBUG: {self.name} decided to use {self.intention.__class__.__name__}")
            return self.intention.__class__.__name__
        else:
            print(f"WARNING: {self.name} has no abilities")
            self.intention_icon_types = [IconType.UNKNOWN]
            return "No Action"

    @staticmethod
    def generate(level: int, is_boss: bool = False, monster_type: Optional[str] = None):
        if is_boss:
            # selected_monster_type = next(mt for mt in Monster.boss_types if mt.name == monster_type)
            selected_monster_type = random.choices(
                Monster.boss_types,
                weights=[1 / mt.rarity for mt in Monster.boss_types],
                k=1,
            )[0]
        else:
            if monster_type:
                selected_monster_type = next(mt for mt in Monster.monster_types if mt.name == monster_type)
            else:
                selected_monster_type = random.choices(
                    Monster.monster_types,
                    weights=[1 / mt.rarity for mt in Monster.monster_types],
                    k=1,
                )[0]

        base_health = 12 + math.log(level + 1, 3) * 8
        base_damage = 6 + math.log(level + 1, 3) * 3
        base_spell_power = 6 + math.log(level + 1, 3) * 3

        health = round(
            base_health * selected_monster_type.health_mult * random.uniform(0.9, 1.1)
        )
        damage = round(
            base_damage * selected_monster_type.damage_mult * random.uniform(0.9, 1.1)
        )
        spell_power = round(
            base_spell_power * selected_monster_type.spell_power_mult * random.uniform(0.9, 1.1)
        )

        image_path = f"./assets/images/characters/{selected_monster_type.name.lower().replace(' ', '_')}.png"

        return Monster(
            selected_monster_type.name,
            health,
            damage,
            spell_power,
            image_path,
            selected_monster_type.symbol,
            monster_type=selected_monster_type,
            is_boss=is_boss,
            level=level,
        )

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
            "intention": self.intention.__class__.__name__ if self.intention else None,
            "monster_level_limits" : self.monster_type.monster_level_limits if self.monster_type else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Monster":
        monster_type = next(
            (
                mt
                for mt in cls.monster_types + cls.boss_types
                if mt.name == data["monster_type"]
            ),
            None,
        )
        monster = cls(
            data["name"],
            data["max_health"],
            data["damage"],
            data["spell_power"],
            data["image_path"],
            data["symbol"],
            health=data["max_health"],
            shields=data["shields"],
            shake=data["shake"],
            selected=data["selected"],
            is_boss=data["is_boss"],
            monster_type=monster_type,
            level=data["level"],
        )
        monster.status_effects = StatusEffectManager.from_dict(data["status_effects"])
        monster.power_rating = data["power_rating"]
        if data["intention"]:
            monster.intention = next((a for a in monster.monster_type.abilities if a.__class__.__name__ == data["intention"]), None)
        return monster

    def diminish_effects_at_turn_start(self):
        self.status_effects.diminish_effects_at_turn_start()
