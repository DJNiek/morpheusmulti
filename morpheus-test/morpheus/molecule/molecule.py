from pathlib import Path
from typing import Optional

import rdkit.Chem as _rdc
from rdkit.Chem import AllChem as _rdca

from morpheus.molecule.smiles import CanonicalSmiles, Smiles
from morpheus.simulation.options import ConformerSearchMethod
from morpheus.simulation.instance import SimulationInstance
from morpheus.interfaces.delta_g import IDeltaG

import subprocess


class Molecule(IDeltaG):
    smiles: Smiles
    delta_g: Optional[float]
    __internal_mol: _rdc.Mol

    def __init__(self, smiles: Smiles = "") -> None:
        self.smiles = smiles
        self.delta_g = None
        self.delta_h = None

    def from_molecule(self, molecule: _rdc.Mol):
        self.smiles = _rdc.MolToSmiles(_rdc.RemoveHs(molecule), kekuleSmiles=True)
        self.__internal_mol = molecule
        return self

    def __prepare_molecule(self):
        self.__internal_mol = _rdc.AddHs(_rdc.MolFromSmiles(self.smiles))

    @property
    def prepared_molecule(self) -> _rdc.Mol:
        self.__prepare_molecule()
        return self.__internal_mol

    def __str__(self):
        return self.smiles

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if isinstance(other, Molecule):
            return _rdc.CanonSmiles(self.smiles) == _rdc.CanonSmiles(other.smiles)
        return False

    def obabel_fallback(self) -> _rdc.Mol:
        result = subprocess.run(
            ["obabel", f"-:{self.smiles}", "-oxyz", "-h", "--gen3d"],
            capture_output=True,
        )
        xyz = result.stdout
        mol = _rdc.MolFromXYZBlock(xyz)
        mol = _rdc.Mol(mol)
        _rdc.rdDetermineBonds.DetermineBonds(mol)
        self.__internal_mol = mol
        return self.__internal_mol

    def __embed_molecule(self):
        try:
            _rdca.EmbedMolecule(self.__internal_mol)
        except:
            self.__internal_mol = self.obabel_fallback()
        return self.__internal_mol

    def optimize_molecule_rdkit(self, instance: SimulationInstance):
        conformer_search_options = instance.options.conformer_search
        params = _rdca.ETDG()
        conformer_ids = _rdca.EmbedMultipleConfs(
            self.__internal_mol,
            numConfs=conformer_search_options.accuracy,
            params=params,
        )

        # fallback if rdkit fails
        if len(conformer_ids) == 0:
            self.obabel_fallback()
            return

        energies = []
        for conf_id in conformer_ids:
            _rdca.UFFOptimizeMolecule(self.__internal_mol, confId=conf_id)
            energy = _rdca.UFFGetMoleculeForceField(
                self.__internal_mol, confId=conf_id
            ).CalcEnergy()
            energies.append(energy)
        self.__internal_mol = _rdc.Mol(
            self.__internal_mol, confId=energies.index(min(energies))
        )
        _rdca.MMFFOptimizeMolecule(self.__internal_mol)

    def optimize_molecule_crest(self, instance: SimulationInstance):
        self.__embed_molecule()
        _rdca.MMFFOptimizeMolecule(self.__internal_mol)
        _rdc.MolToXYZFile(self.__internal_mol, Path(f"{instance.inp_path}"))
        subprocess.Popen(
            [
                "crest",
                instance.inp_path,
                "-v3",
                "-chrg",
                "0",
                "-uhf",
                "0",
                "--T",
                f"{instance.options.xtb_cores}",
                f"-gfn{instance.options.conformer_search.accuracy.value}",
            ],
            cwd=instance.tmp_path,
            # stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        ).wait()

        self.__internal_mol = _rdc.MolFromXYZFile(
            Path(f"{instance.tmp_path}/crest_best.xyz").__str__()
        )

    def optimize_molecule(self, instance: SimulationInstance):
        conformer_search_options = instance.options.conformer_search
        match conformer_search_options.method:
            case ConformerSearchMethod.RDKIT:
                self.optimize_molecule_rdkit(instance)
                return
            case ConformerSearchMethod.CREST:
                self.optimize_molecule_crest(instance)
                return
            case _:
                raise NotImplemented(
                    f"Method {conformer_search_options.method.value} is not yet implemented. "
                )

    @property
    def canonical(self) -> CanonicalSmiles:
        return CanonicalSmiles(self.smiles)

    def calculate_delta_g(self, instance: SimulationInstance) -> float:
        return instance.cache.read(self.canonical) or instance.cache.write(
            self.canonical, self.calculate_delta_g_real(instance)
        )

    def calculate_delta_g_real(self, instance: SimulationInstance) -> float:
        self.__prepare_molecule()

        self.__embed_molecule()
        if instance.options.conformer_search:
            self.optimize_molecule(instance)
        else:
            self.__embed_molecule()
            _rdca.MMFFOptimizeMolecule(self.__internal_mol)

        instance.generate_inp_file(_rdc.MolToXYZBlock(self.__internal_mol))

        return instance.calculate_delta_g()
