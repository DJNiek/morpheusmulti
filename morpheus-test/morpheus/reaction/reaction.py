from rdkit.Chem import rdChemReactions
from typing import Optional

from morpheus.interfaces.delta_g import IDeltaG
from morpheus.molecule.molecule import Molecule
from morpheus.simulation import Simulation, SimulationInstance
from morpheus.molecule.smiles import Smiles
from morpheus.utils.units import EnergyUnit, EnergyValue


class ReactionProducts(IDeltaG):
    reactants: list[Molecule]
    products: list[Molecule]
    delta_g: Optional[float]

    def __init__(self, reactants: list[Molecule], products: list[Molecule]):
        self.reactants = reactants
        self.products = products
        self.delta_g = None
        self.delta_h = None

    def __repr__(self) -> str:
        return f'{str.join(" + ", [f"{product}" for product in self.products])}    ΔG = {EnergyValue(self.delta_g, EnergyUnit.Eh).to(EnergyUnit.kJMol) if self.delta_g else "?"}    ΔH = {EnergyValue(self.delta_h, EnergyUnit.Eh).to(EnergyUnit.kJMol) if self.delta_h else "?"}'

    def calculate_delta_g(
        self,
        instance: SimulationInstance,
    ) -> tuple[float, float]:
        simulation = Simulation(instance.options)

        substrate_delta_g = sum(
            list(
                map(
                    lambda substrate: simulation.calculate_delta_g(substrate)[0],
                    self.reactants,
                )
            )
        )
        product_delta_g = sum(
            list(
                map(
                    lambda product: simulation.calculate_delta_g(product)[0],
                    self.products,
                )
            )
        )
        self.delta_g = product_delta_g - substrate_delta_g

        substrate_delta_h = sum(
            list(
                map(
                    lambda substrate: simulation.calculate_delta_g(substrate)[1],
                    self.reactants,
                )
            )
        )
        product_delta_h = sum(
            list(
                map(
                    lambda product: simulation.calculate_delta_g(product)[1],
                    self.products,
                )
            )
        )
        self.delta_h = product_delta_h - substrate_delta_h
        return self.delta_g, self.delta_h


class ReactionTemplate:
    reaction: rdChemReactions.ChemicalReaction

    def __init__(self, smarts: str):
        try:
            self.reaction = rdChemReactions.ReactionFromSmarts(smarts)
        except:
            raise ValueError(f"Invalid SMARTS {smarts}")

    def check_reactants(self, reactants: list[Molecule]) -> bool:
        return self.get_num_reactants() == len(reactants)

    def run_reaction(self, reactants: list[Molecule]) -> Optional[ReactionProducts]:
        if not self.check_reactants(reactants):
            raise ValueError(
                f"Wrong number of reactants, expected {self.get_num_reactants()} but got {len(reactants)}"
            )

        possible_products = self.reaction.RunReactants(
            [reactant.prepared_molecule for reactant in reactants]
        )

        if possible_products:
            return list(
                map(
                    lambda products: ReactionProducts(
                        reactants,
                        list(
                            map(
                                lambda product: Molecule().from_molecule(product),
                                products,
                            )
                        ),
                    ),
                    possible_products,
                )
            )
        return None

    def get_num_reactants(self) -> int:
        return len(self.reaction.GetReactants())


class Reaction(ReactionTemplate):
    reaction: rdChemReactions.ChemicalReaction
    reactants: list[Molecule]
    products: Optional[list[ReactionProducts]]
    delta_gs: Optional[list[float]]

    def __init__(self, reaction_template: ReactionTemplate):
        self.reaction = reaction_template.reaction
        self.reactants = []
        self.products = None
        self.delta_gs = None

    def add_reactants(self, reactants: list[Smiles]):
        if not type(reactants) == type([]) and type(reactants[0] == type(Smiles(""))):
            raise ValueError(f"add_reactants takes a list[Smiles], not {type(reactants)}")
        if self.check_reactants(reactants):
            self.reactants = list(map(lambda r: Molecule(r), reactants))
        else:
            raise ValueError(
                f"Invalid number of reactants, expected {self.get_num_reactants()} but got {len(reactants)}"
            )

    def run_reaction(self) -> list[ReactionProducts] | None:
        if not self.reactants:
            raise ValueError("Missing reactants")
        if self.check_reactants(self.reactants):
            self.products = super().run_reaction(self.reactants)
            return self.products

    def calculate_delta_gs(self) -> list[float]:
        self.delta_gs = []
        pass


__all__ = ["Reaction", "ReactionTemplate"]
