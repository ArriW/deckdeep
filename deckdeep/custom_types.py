from dataclasses import dataclass
from enum import Enum, auto

class TriggerWhen(Enum):
    COMBAT_START = auto()
    COMBAT_END = auto()
    TURN_START = auto()
    TURN_END = auto()
    BEFORE_ATTACK = auto()
    AFTER_ATTACK = auto()
    ON_DAMAGE_TAKEN = auto()
    ON_DAMAGE_DEALT = auto()
    PERMANENT = auto()

@dataclass(frozen=True)
class Health:
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Health cannot be negative")

    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)

    def __truediv__(self, other):
        if isinstance(other, Health):
            return self.value / other.value
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __mul__(self, other):
        if isinstance(other, Health):
            return self.value * other.value
        return self.value * other

    def __rmul__(self, other):
        return self * other

    def __eq__(self, other):
        if isinstance(other, Health):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other):
        if isinstance(other, Health):
            return self.value < other.value
        return self.value < other

    def __le__(self, other):
        if isinstance(other, Health):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other):
        if isinstance(other, Health):
            return self.value >= other.value
        return self.value >= other

    def __gt__(self, other):
        if isinstance(other, Health):
            return self.value > other.value
        return self.value > other

    def __add__(self, other):
        if isinstance(other, Health):
            return Health(self.value + other.value)
        return Health(self.value + other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, Health):
            return Health(max(0, self.value - other.value))
        return Health(max(0, self.value - other))

    def __rsub__(self, other):
        return Health(max(0, other - self.value))

    def to_dict(self):
        return self.value

    @classmethod
    def from_dict(cls, data):
        return cls(data)


@dataclass(frozen=True)
class Energy:
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Energy cannot be negative")

    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)

    def __truediv__(self, other):
        if isinstance(other, Energy):
            return self.value / other.value
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __mul__(self, other):
        if isinstance(other, Energy):
            return self.value * other.value
        return self.value * other

    def __rmul__(self, other):
        return self * other

    def __eq__(self, other):
        if isinstance(other, Energy):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other):
        if isinstance(other, Energy):
            return self.value < other.value
        return self.value < other

    def __le__(self, other):
        if isinstance(other, Energy):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other):
        if isinstance(other, Energy):
            return self.value >= other.value
        return self.value >= other

    def __gt__(self, other):
        if isinstance(other, Energy):
            return self.value > other.value
        return self.value > other

    def __add__(self, other):
        if isinstance(other, Energy):
            return Energy(self.value + other.value)
        return Energy(self.value + other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, Energy):
            return Energy(max(0, self.value - other.value))
        return Energy(max(0, self.value - other))

    def __rsub__(self, other):
        return Energy(max(0, other - self.value))

    def to_dict(self):
        return self.value

    @classmethod
    def from_dict(cls, data):
        return cls(data)
