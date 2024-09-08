from typing import Dict, Any, List
from enum import Enum


class TriggerType(Enum):
    TURN_START = 1
    TURN_END = 2
    BEFORE_ATTACK = 3
    AFTER_ATTACK = 4
    ON_DAMAGE_TAKEN = 5
    ON_HEAL = 6


class StatusEffect:
    def __init__(self, name: str, value: int, stack: bool, type: str):
        self.name = name
        self.value = value
        self.stack = stack
        self.type = type
        self.triggers: List[TriggerType] = []

    def apply(self, target: Any) -> None:
        pass

    def is_expired(self) -> bool:
        return self.value <= 0

    def on_trigger(self, trigger_type: TriggerType, target: Any) -> None:
        pass

    def diminish(self) -> None:
        self.value = max(0, self.value - 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "stack": self.stack,
            "type": self.type,
            "triggers": [t.value for t in self.triggers],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusEffect":
        effect = cls(data["name"], data["value"], data["stack"], data["type"])
        effect.triggers = [TriggerType(t) for t in data["triggers"]]
        return effect


class Bleed(StatusEffect):
    def __init__(self, value: int):
        super().__init__("Bleed", value=value, stack=True, type="debuff")
        self.triggers = [TriggerType.TURN_START]

    def on_trigger(self, trigger_type: TriggerType, target: Any) -> None:
        if trigger_type == TriggerType.TURN_START:
            damage = self.value
            target.take_damage(damage)
            self.diminish()


class HealthRegain(StatusEffect):
    def __init__(self, value: int):
        super().__init__("HealthRegain", value=value, stack=True, type="buff")
        self.triggers = [TriggerType.TURN_START]

    def on_trigger(self, trigger_type: TriggerType, target: Any) -> None:
        if trigger_type == TriggerType.TURN_START:
            target.heal(self.value)
            self.diminish()


class EnergyBonus(StatusEffect):
    def __init__(self, value: int):
        super().__init__("EnergyBonus", value=value, stack=False, type="buff")
        self.triggers = [TriggerType.TURN_START]

    def on_trigger(self, trigger_type: TriggerType, target: Any) -> None:
        if trigger_type == TriggerType.TURN_START:
            target.bonus_energy += self.value
            self.value = 0


class Weakness(StatusEffect):
    def __init__(self, value: int):
        super().__init__("Weakness", value=value, stack=True, type="debuff")
        self.triggers = [TriggerType.BEFORE_ATTACK, TriggerType.TURN_END]

    def on_trigger(self, trigger_type: TriggerType, target: Any) -> None:
        if trigger_type == TriggerType.TURN_END:
            self.diminish()


class Bolster(StatusEffect):
    def __init__(self, value: int):
        super().__init__("Bolster", value=value, stack=True, type="buff")
        self.triggers = [TriggerType.ON_DAMAGE_TAKEN, TriggerType.TURN_END]

    def on_trigger(self, trigger_type: TriggerType, target: Any) -> None:
        if trigger_type == TriggerType.TURN_END:
            self.diminish()


class Burn(StatusEffect):
    def __init__(self, value: int):
        super().__init__("Burn", value=value, stack=True, type="debuff")
        self.triggers = [TriggerType.TURN_START]

    def on_trigger(self, trigger_type: TriggerType, target: Any) -> None:
        if trigger_type == TriggerType.TURN_START:
            if self.value >= 3:
                damage = self.value * 4
                target.take_damage(damage)
                self.value = 0
            else:
                self.diminish()


class StatusEffectManager:
    def __init__(self):
        self.effects: List[StatusEffect] = []

    def add_effect(self, effect: StatusEffect) -> None:
        existing_effect = next((e for e in self.effects if e.name == effect.name), None)
        if existing_effect:
            if effect.stack:
                existing_effect.value += effect.value
            else:
                existing_effect.value = max(existing_effect.value, effect.value)
        else:
            self.effects.append(effect)

    def trigger_effects(self, trigger_type: TriggerType, target: Any) -> None:
        for effect in list(self.effects):
            if trigger_type in effect.triggers:
                effect.on_trigger(trigger_type, target)
            if effect.is_expired():
                self.effects.remove(effect)

    def clear_effects(self) -> None:
        self.effects = []

    def clear_debuff(self) -> None:
        self.effects = [effect for effect in self.effects if effect.type != "debuff"]

    def clear_buff(self) -> None:
        self.effects = [effect for effect in self.effects if effect.type != "buff"]

    def to_dict(self) -> Dict[str, Any]:
        return {"effects": [effect.to_dict() for effect in self.effects]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusEffectManager":
        manager = cls()
        manager.effects = [
            StatusEffect.from_dict(effect_data) for effect_data in data["effects"]
        ]
        return manager
