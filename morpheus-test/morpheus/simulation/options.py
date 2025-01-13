from enum import Enum
import os
from typing import Optional
from pathlib import Path

from morpheus.utils import information

from enum import Enum


class GFNLevel(Enum):
    GFNFF = "ff"
    GFN0 = "0"
    GFN1 = "1"
    GFN2 = "2"


class ConformerSearchMethod(Enum):
    RDKIT = "rdkit"
    CREST = "crest"


class ConformerSearchOptions:
    method: ConformerSearchMethod
    accuracy: int | GFNLevel

    def __init__(
        self,
        method: ConformerSearchMethod = ConformerSearchMethod.RDKIT,
        rdkit_level: int = 200,
        crest_level: GFNLevel = GFNLevel.GFN0,
    ) -> None:
        self.method = method
        match self.method:
            case ConformerSearchMethod.RDKIT:
                self.accuracy = rdkit_level
                return
            case ConformerSearchMethod.CREST:
                self.accuracy = crest_level


class Solvent(Enum):
    ACETONE = "acetone"
    ACETONITRILE = "acetonitrile"
    ANILINE = "aniline"
    BENZALDEHYDE = "benzaldehyde"
    BENZENE = "benzene"
    DIOXANE = "dioxane"
    DMF = "dmf"
    DMSO = "dmso"
    ETHER = "ether"
    ETHYLACETATE = "ethylacetate"
    FURANE = "furane"
    HEXADECANE = "hexadecane"
    HEXANE = "hexane"
    METHANOL = "methanol"
    NITROMETHANE = "nitromethane"
    OCTANOL = "octanol"
    PHENOL = "phenol"
    TOLUENE = "toluene"
    THF = "thf"
    WATER = "water"

    def __get_solvents() -> list:
        solvents = []
        for _p, v in vars(Solvent).items():
            try:
                v.value
                solvents.append(v)
            except:
                pass
        return solvents

    def solvents():
        values = []
        for solvent in Solvent.__get_solvents():
            try:
                values.append(solvent.value)
            except:
                pass
        return values

    def from_string(s: str):
        if s:
            for solvent in Solvent.__get_solvents():
                try:
                    if solvent.value == s:
                        return solvent
                except:
                    pass
        return None


class SimulationOptions:
    gfn_level: GFNLevel
    xtb_cores: int
    conformer_search: Optional[ConformerSearchOptions]
    tmp_path: Path
    solvent: Optional[Solvent]

    def __init__(
        self,
        gfn_level: GFNLevel = GFNLevel.GFN0,
        xtb_cores: int = os.cpu_count(),
        conformer_search_options=None,
        tmp_path: Path = information.TMP_DIR,
        solvent: Solvent = None,
    ) -> None:
        self.gfn_level = gfn_level
        self.xtb_cores = xtb_cores or 1
        self.conformer_search = conformer_search_options
        self.tmp_path = tmp_path
        self.solvent = solvent

    def __repr__(self) -> str:
        return f"""GFN level: {self.gfn_level.value}
xtb cores: {self.xtb_cores}
{'' if not self.conformer_search else f'''Conformer search:
  method: {self.conformer_search.method}
  iterations: {self.conformer_search.accuracy}
'''}
"""


DEFAULT_SIMULATION_OPTIONS = SimulationOptions()
