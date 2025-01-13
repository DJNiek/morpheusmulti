from pathlib import Path
from typing import Optional

from morpheus.molecule import Smiles
from morpheus.simulation.options import ConformerSearchOptions, GFNLevel, Solvent
from morpheus.reaction import ReactionTemplate

from enum import Enum


class FileFormat(Enum):
    JSON = "json"
    CSV = "csv"
    def from_string(f: str):
        match f:
            case "json": 
                return FileFormat.JSON
            case "csv": 
                return FileFormat.CSV
    
class Options:
    reaction: ReactionTemplate
    output_path: Path
    output_formats: list[FileFormat]
    xtb_gfn: GFNLevel
    conformer_search: Optional[ConformerSearchOptions]
    cores: int
    xtb_cores: int
    reactants: list[list[Smiles]]
    solvent: Optional[Solvent]

    def __init__(
        self,
        reactants: list[list[Smiles]],
        output_path: Path,
        xtb_gfn: GFNLevel,
        conformer_search: Optional[ConformerSearchOptions],
        cores: int,
        xtb_cores: int,
        reaction: ReactionTemplate,
        output_formats: list[FileFormat] = [],
        solvent: Optional[Solvent] = None
    ) -> None:
        self.output_path = output_path
        self.conformer_search = conformer_search
        self.cores = cores
        self.xtb_gfn = xtb_gfn
        self.xtb_cores = xtb_cores
        self.reaction = reaction
        self.reactants = reactants
        self.output_formats = output_formats
        self.solvent = solvent
