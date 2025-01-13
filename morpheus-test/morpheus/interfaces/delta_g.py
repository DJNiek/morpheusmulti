from abc import ABC, abstractmethod

from morpheus.simulation.instance import SimulationInstance

class IDeltaG(ABC):
  @abstractmethod
  def calculate_delta_g(self, instance: SimulationInstance) -> float:
    pass
