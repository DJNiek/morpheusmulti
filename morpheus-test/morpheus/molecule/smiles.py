from rdkit import Chem as rdc

class Smiles(str):
  smiles_string: str
  
  def __init__(self, smiles: str) -> None:
    if not rdc.MolFromSmiles(smiles, sanitize=False):
      raise ValueError(f"Invalid SMILES: {smiles}")
    else:
      self.smiles_string = smiles

  def __str__(self) -> str:
    return self.smiles_string

class CanonicalSmiles(Smiles):
  def __init__(self, smiles: Smiles) -> None:
    self.smiles_string = rdc.CanonSmiles(smiles)