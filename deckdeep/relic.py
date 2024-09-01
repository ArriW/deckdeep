import random
from enum import Enum
from typing import Dict, Callable


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
    def __init__(
        self, name: str, description: str, effect: Callable, trigger_when: TriggerWhen
    ):
        self.name = name
        self.description = description
        self.effect = effect
        self.trigger_when = trigger_when
        self.triggered_once = False

    def apply_effect(self, player, game) -> str:

        if self.trigger_when == TriggerWhen.PERMANENT:
            if not self.triggered_once:
                self.effect(player, game)
                self.triggered_once = True
                return f"Permanet {self.name} {self.description}"
        else:
            self.effect(player, game)
            return f"{self.name} triggered!"
        return "Did not trigger"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "trigger_when": self.trigger_when.value,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Relic":
        return cls(
            name=data["name"],
            description=data["description"],
            effect=lambda p, g: None,  # We can't serialize functions, so we use a dummy function
            trigger_when=TriggerWhen(data["trigger_when"]),
        )

    @staticmethod
    def generate_relic_pool(num_relics):
        return random.sample(
            list(ALL_RELICS.values()), min(num_relics, len(ALL_RELICS))
        )


ALL_RELICS = {
    "Hair of the Dog": Relic(
        "Hair of the Dog",
        "+10 max HP.",
        lambda p, g: p.increase_max_health(10),
        TriggerWhen.PERMANENT,
    ),
    "Cursed Coin": Relic(
        "Cursed Coin",
        "Your attacks deal 1 additional damage.",
        lambda p, g: setattr(p, "strength", p.strength + 1),
        TriggerWhen.PERMANENT,
    ),
    "Healing Charm": Relic(
        "Healing Charm",
        "Heal 5 HP at the start of each combat.",
        lambda p, g: p.heal(5),
        TriggerWhen.START_OF_COMBAT,
    ),
    "Energy Crystal": Relic(
        "Energy Crystal",
        "Start each combat with 1 additional energy.",
        lambda p, g: setattr(p, "energy", p.energy + 1),
        TriggerWhen.START_OF_COMBAT,
    ),
    "Strength Amulet": Relic(
        "Strength Amulet",
        "Your attacks deal 2 additional damage.",
        lambda p, g: setattr(p, "strength", p.strength + 2),
        TriggerWhen.PERMANENT,
    ),
    "Shield Rune": Relic(
        "Shield Rune",
        "Gain 3 block at the start of each turn.",
        lambda p, g: p.add_block(3),
        TriggerWhen.START_OF_TURN,
    ),
    "Lucky Coin": Relic(
        "Lucky Coin",
        "10% chance to dodge enemy attacks.",
        lambda p, g: setattr(p, "dodge_chance", p.dodge_chance + 0.1),
        TriggerWhen.PERMANENT,
    ),
    "Paper Weight": Relic(
        "Paper Weight",
        "Draw 1 additional card at the start of each turn. At the cost of permanet energy.",
        lambda p, g: (
            setattr(p, "cards_per_turn", p.cards_per_turn + 1),
            setattr(p, "energy", p.max_energy - 1),
        ),
        TriggerWhen.PERMANENT,
    ),
    "Phoenix Feather": Relic(
        "Phoenix Feather",
        "Once, survive a fatal blow with 1 HP.",
        lambda p, g: setattr(p, "phoenix_feather_active", True),
        TriggerWhen.PERMANENT,
    ),
    "Cursed Dagger": Relic(
        "Cursed Dagger",
        "Deal 10 damage to a random enemy at the start of each turn.",
        lambda p, g:  g.monster_group.random_monster() and g.monster_group.random_monster().take_damage(10),
        TriggerWhen.START_OF_TURN,
    ),
    "Time Warp": Relic(
        "Time Warp",
        "12% chance to take an extra turn after your turn ends.",
        lambda p, g: setattr(p, "extra_turn_chance", 0.12),
        TriggerWhen.PERMANENT,
    ),
}


def get_relic_by_name(name: str) -> Relic:
    try:
        return ALL_RELICS[name]
    except:
        raise KeyError(f"Relic '{name}' not found in ALL_RELICS")
