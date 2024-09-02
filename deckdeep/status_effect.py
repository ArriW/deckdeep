from typing import Dict, Any


class StatusEffect:
    def __init__(self, name: str, value: int, stack: bool, type: str):
        self.name = name
        self.value = value
        self.stack = stack
        self.type = type

    def apply(self, target: Any) -> None:
        pass

    def is_expired(self) -> bool:
        return self.value <= 0

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "value": self.value}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusEffect":
        return cls(**data)


class Bleed(StatusEffect):
    def __init__(self, value: int):
        super().__init__("Bleed", value=value, stack=True, type="debuff")

    def apply(self, target: Any) -> None:
        damage = self.value
        target.take_damage(damage)
        self.value = max(0, self.value - 1)

    def is_expired(self) -> bool:
        return self.value <= 0


class HealthRegain(StatusEffect):
    def __init__(self, value: int):
        super().__init__("HealthRegain", value=value, stack=True, type="buff")

    def apply(self, target: Any) -> None:
        target.heal(self.value)
        self.value = max(0, self.value - 1)

    def is_expired(self) -> bool:
        return self.value <= 0


class EnergyBonus(StatusEffect):
    def __init__(self, value: int):
        super().__init__("EnergyBonus", value=value, stack=False, type="buff")

    def apply(self, target: Any) -> None:
        target.energy += self.value
        self.value = max(0, self.value - 1)


class StatusEffectManager:
    def __init__(self):
        self.effects = []

    def add_effect(self, effect: StatusEffect) -> None:
        existing_effect = next((e for e in self.effects if e.name == effect.name), None)
        if existing_effect:
            if effect.stack:
                existing_effect.value += effect.value
            else:
                existing_effect.value = max(existing_effect.value, effect.value)
        else:
            self.effects.append(effect)

    def apply_effects(self, target: Any) -> None:
        for effect in list(self.effects):
            effect.apply(target)
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
        manager.effects = [StatusEffect.from_dict(effect_data) for effect_data in data["effects"]]
        return manager
