import pytest

from morpheus.molecule import Smiles, Molecule

def test_smiles():
  benzene = Smiles("C1=CC=CC=C1")
  assert benzene.smiles_string == "C1=CC=CC=C1"
  with pytest.raises(ValueError) as _:
    Smiles("this should be invalid")

def test_molecule():
  benzene = Molecule(Smiles("C1=CC=CC=C1"))
  assert benzene.smiles == Smiles("C1=CC=CC=C1")
  assert benzene.delta_g == None
  assert benzene.__str__() == "C1=CC=CC=C1"
  assert Molecule().from_molecule(benzene.prepared_molecule).smiles == Smiles("C1=CC=CC=C1")