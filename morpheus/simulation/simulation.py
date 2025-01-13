from morpheus.simulation.cache import SimulationCache
from morpheus.simulation.options import DEFAULT_SIMULATION_OPTIONS, SimulationOptions
from morpheus.simulation.instance import SimulationInstance
from morpheus.interfaces.delta_g import IDeltaG

class Simulation:
    options: SimulationOptions
    cache: SimulationCache

    def __init__(self, options: SimulationOptions=DEFAULT_SIMULATION_OPTIONS):
        self.options = options
        self.cache = SimulationCache()

    def calculate_delta_g(self, obj: IDeltaG) -> tuple[float, float]:
        instance = SimulationInstance(self.options, self.cache)
        instance.result_g, instance.result_h = obj.calculate_delta_g(instance)
        return instance.result_g, instance.result_h
