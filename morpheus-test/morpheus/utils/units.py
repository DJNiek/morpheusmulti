from enum import Enum


class EnergyUnit(Enum):
    Eh = 1
    kJMol = 2625.4996394799
    kCalMol = 2625.4996394799 / 4.183
    def __str__(self):
        match self:
            case EnergyUnit.Eh:
                return "Eh"
            case EnergyUnit.kJMol:
                return "kJ/mol"
            case EnergyUnit.kCalMol:
                return "kcal/mol"
class EnergyValue:
    value: float
    unit: EnergyUnit

    def __init__(self, value: float, unit: EnergyUnit) -> None:
        self.value = value
        self.unit = unit

    def __str__(self) -> str:
        return f"{self.value} {self.unit.__str__()}"

    def __add__(self, other):
        if isinstance(other, EnergyValue):
            return EnergyValue(
                self.value + other.value * (self.unit.value / other.unit.value),
                self.unit,
            )

    def __sub__(self, other):
        if isinstance(other, EnergyValue):
            return EnergyValue(
                self.value - other.value * (self.unit.value / other.unit.value),
                self.unit,
            )

    def __truediv__(self, other):
        if isinstance(other, EnergyValue):
            return self.value / (other.value * (self.unit.value / other.unit.value))
        else:
            return EnergyValue(self.value / other, self.unit)

    def __mul__(self, other: float):
        if not isinstance(other, EnergyValue):
            return EnergyValue(self.value * other, self.unit)

    def __neg__(self):
        return self.__mul__(-1)

    def to(self, unit: EnergyUnit):
        return EnergyValue(self.value * (unit.value / self.unit.value), unit)

def convert(self, from_unit: EnergyUnit, to_unit: EnergyUnit):
    return self * (to_unit.value/from_unit.value)