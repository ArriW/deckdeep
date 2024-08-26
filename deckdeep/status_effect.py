from typing import Dict, Any

class StatusEffect:
    def __init__(self, name: str, value: int, stack: bool):
        self.name = name
        self.value = value
        self.stack = stack 

    def apply(self, target: Any) -> None:
        pass
    def is_expired(self) -> bool:
        return self.value <= 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusEffect':
        return cls(**data)

class Bleed(StatusEffect):
    def __init__(self, value: int):
        super().__init__("Bleed", value=value, stack =  True)

    def apply(self, target: Any) -> None:
        damage = self.value
        target.take_damage(damage)
        self.value = max(0, self.value - 1) 

    def is_expired(self) -> bool:
        return self.value <= 0

class HealthRegain(StatusEffect):
    def __init__(self, value: int):
        super().__init__("HealthRegain", value=value, stack= True)

    def apply(self, target: Any) -> None:
        target.heal(self.value)
        self.value = max(0, self.value - 1) 

    def is_expired(self) -> bool:
        return self.value <= 0


class EnergyBonus(StatusEffect):
    def __init__(self, value: int):
        super().__init__("EnergyBonus", value=value, stack = False)
    def apply(self, target: Any) -> None:
        target.energy += self.value
        self.value = max(0, self.value - 1)

class StatusEffectManager:
    def __init__(self):
        self.effects: Dict[str, StatusEffect] = {}

    def add_effect(self, effect: StatusEffect) -> None:
        if effect.name in self.effects.keys():
            if effect.stack:
                self.effects[effect.name].value += effect.value 
            else:
                self.effects[effect.name].value = max(self.effects[effect.name].value,effect.value)
        else:
            self.effects[effect.name] = effect

    def apply_effects(self, target: Any) -> None:
        for effect in list(self.effects.values()):
            effect.apply(target)
            if effect.is_expired():
                del self.effects[effect.name]

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {name: effect.to_dict() for name, effect in self.effects.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> 'StatusEffectManager':
        manager = cls()
        for effect_data in data.values():
            effect_class = globals()[effect_data["name"]]
            del effect_data["name"]
            manager.add_effect(effect_class.from_dict(effect_data))
        return manager