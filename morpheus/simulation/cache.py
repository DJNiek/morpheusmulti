from morpheus.molecule.smiles import CanonicalSmiles

class SimulationCache:
  __cache: dict[str, float]
  def __init__(self) -> None:
    self.__cache = {}
  
  def read(self, key: CanonicalSmiles) -> float:
    return self.__cache.get(key.__str__())
  
  def write(self, key: CanonicalSmiles, value: float) -> float:
    self.__cache[key] = value
    return value