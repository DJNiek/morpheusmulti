from io import StringIO
from typing import Optional
import pandas as pd

from morpheus.cli.parser.options import FileFormat, Options
from morpheus.simulation.options import ConformerSearchMethod, SimulationOptions
from morpheus.molecule import Smiles
from morpheus.utils.units import EnergyValue, EnergyUnit


class ReactionOutput:
    reactants: list[Smiles]
    products: list[Smiles]
    delta_g: EnergyValue

    def __init__(
        self, reactants: list[Smiles], products: list[Smiles], delta_g: EnergyValue
    ) -> None:
        self.reactants = reactants
        self.products = products
        self.delta_g = delta_g


class Output:
    options: Options
    reactions: list[ReactionOutput]
    df: Optional[pd.DataFrame]
    stdout: str

    def __init__(self, options: Options) -> None:
        self.options = options

        self.reactions = []
        self.df = None
        self.stdout = ""

    def write(self, s):
        self.stdout += f"{s}\n"

    def add_reaction(
        self, reactants: list[Smiles], products: list[Smiles], delta_g: EnergyValue
    ) -> None:
        self.reactions.append(ReactionOutput(reactants, products, delta_g))

    def generate_options(self) -> str:
        l = f"""Morpheus
gfn level: {self.options.gfn_level.name.lower()}
xtb parallel cores: {self.options.xtb_cores}"""
        if self.options.solvent:
            l += """solvent: {self.options.solvent.value}"""
        if self.options.conformer_search:
            l += f"""conformer search:
    method: {self.options.conformer_search.method.name}
            """
            match self.options.conformer_search.method:
                case ConformerSearchMethod.RDKIT:
                    l += f"   number of conformers: {self.options.conformer_search.accuracy}"
                case ConformerSearchMethod.CREST:
                    l += f"   gfn level: {self.options.conformer_search.accuracy.name.lower()}"
        return l

    def generate_table(self) -> pd.DataFrame:
        """generate table from provided reaction products

        Returns:
            pandas data frame
        """

        data = {
            f"reactants": list(
                map(
                    lambda reaction_output: list(
                        map(
                            lambda reactant: reactant.__str__(),
                            reaction_output.reactants,
                        )
                    ),
                    self.reactions,
                )
            ),
            "products": list(
                map(
                    lambda reaction_output: list(
                        map(lambda product: product.__str__(), reaction_output.products)
                    ),
                    self.reactions,
                )
            ),
            f"delta_g ({EnergyUnit.Eh.name})": list(
                map(
                    lambda reaction: reaction.delta_g.to(EnergyUnit.Eh).value,
                    self.reactions,
                )
            ),
        }
        df = pd.DataFrame(data)
        self.df = df
        return df

    def data_as(self, format: FileFormat) -> str:
        data_buffer = StringIO()
        if not type(self.df) == type(None):
            match format:
                case FileFormat.JSON:
                    self.df.to_json(data_buffer, index=False)
                case FileFormat.CSV:
                    self.df.to_csv(data_buffer)
        return data_buffer.getvalue()
