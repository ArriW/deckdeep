import random
from enum import Enum
from typing import Dict
from copy import deepcopy
import uuid


class TriggerWhen(Enum):
    START_OF_TURN = 0
    END_OF_TURN = 1
    START_OF_COMBAT = 2
    END_OF_COMBAT = 3
    ON_ATTACK = 4
    ON_DAMAGE_TAKEN = 5
    ON_DEATH = 6
    PERMANENT = 7


class Relic:
    def __init__(self, name: str, data: Dict):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = data["description"]
        self.effect = data["effect"]
        self.trigger_when = data["trigger_when"]
        self.has_been_applied = False

    def apply_effect(self, player, game) -> str:
        if self.trigger_when == TriggerWhen.PERMANENT:
            if not player.has_applied_permanent_effect(self.name, self.id):
                self.effect(player, game)
                player.add_applied_permanent_effect(self.name, self.id)
                return f"Applied permanent effect: {self.name}"
            return f"Permanent effect already applied for this instance: {self.name}"
        else:
            return self.effect(player, game) or f"{self.name} triggered!"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,  # Add this line
            "name": self.name,
            "description": self.description,
            "trigger_when": self.trigger_when.value,
            "has_been_applied": self.has_been_applied,
        }

    def reset_application_status(self):
        self.has_been_applied = False

    @classmethod
    def from_dict(cls, data: Dict) -> "Relic":
        relic = cls(
            name=data["name"],
            data={
                "description": data["description"],
                "effect": ALL_RELICS[data["name"]][
                    "effect"
                ],  # Get effect from ALL_RELICS
                "trigger_when": TriggerWhen(data["trigger_when"]),
            },
        )
        relic.id = data["id"]  # Add this line
        relic.has_been_applied = data["has_been_applied"]
        return relic

    @staticmethod
    def generate_relic_pool(num_relics):
        selected_relics = random.sample(
            list(ALL_RELICS.items()), min(num_relics, len(ALL_RELICS))
        )
        return [Relic(name, deepcopy(relic)) for name, relic in selected_relics]


ALL_RELICS = {
    "Hair of the Dog": {
        "description": "+10 max HP.",
        "effect": lambda p, g: p.increase_max_health(10),
        "trigger_when": TriggerWhen.PERMANENT,
    },
    "Cursed Coin": {
        "description": "Your attacks deal 1 additional damage.",
        "effect": lambda p, g: p.increase_strength(1),
        "trigger_when": TriggerWhen.PERMANENT,
    },
    "Healing Charm": {
        "description": "Heal 5 HP at the start of each combat.",
        "effect": lambda p, g: p.heal(5),
        "trigger_when": TriggerWhen.START_OF_COMBAT,
    },
    "Energy Crystal": {
        "description": "Start each combat with 1 additional energy.",
        "effect": lambda p, g: p.grant_temporary_energy(1),
        "trigger_when": TriggerWhen.START_OF_COMBAT,
    },
    "Strength Amulet": {
        "description": "Your attacks deal 1 additional damage.",
        "effect": lambda p, g: p.increase_strength(1),
        "trigger_when": TriggerWhen.PERMANENT,
    },
    "Shield Rune": {
        "description": "Gain 3 block at the start of each turn.",
        "effect": lambda p, g: p.add_block(3),
        "trigger_when": TriggerWhen.START_OF_TURN,
    },
    "Lucky Coin": {
        "description": "10% chance to dodge enemy attacks.",
        "effect": lambda p, g: setattr(p, "dodge_chance", p.dodge_chance + 0.1),
        "trigger_when": TriggerWhen.PERMANENT,
    },
    "Paper Weight": {
        "description": "Draw 1 additional card at the start of each turn. At the cost of permanent energy.",
        "effect": lambda p, _: (
            p.increase_cards_per_turn(1),
            p.increase_max_energy(-1, force=True),
        ),
        "trigger_when": TriggerWhen.PERMANENT,
    },
    "Phoenix Feather": {
        "description": "Once, survive a fatal blow with 1 HP.",
        "effect": lambda p, _: setattr(p, "phoenix_feather_active", True),
        "trigger_when": TriggerWhen.PERMANENT,
    },
    "Cursed Dagger": {
        "description": "Deal 10 damage to a random enemy at the start of each turn.",
        "effect": lambda _, g: g
        and g.monster_group
        and g.monster_group.random_monster()
        and g.monster_group.random_monster().take_damage(10)
        or "No valid target for Cursed Dagger",
        "trigger_when": TriggerWhen.START_OF_TURN,
    },
    "Time Warp": {
        "description": "12% chance to take an extra turn after your turn ends.",
        "effect": lambda p, _: setattr(p, "extra_turn_chance", 0.12),
        "trigger_when": TriggerWhen.PERMANENT,
    },
}


def get_relic_by_name(name: str) -> Relic:
    if name not in ALL_RELICS:
        raise KeyError(f"Relic '{name}' not found in ALL_RELICS")
    return Relic(name, ALL_RELICS[name])
