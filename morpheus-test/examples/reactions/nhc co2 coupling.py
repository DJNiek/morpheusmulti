from morpheus.molecule import Molecule
from morpheus.reaction import ReactionTemplate, Reaction
from morpheus.simulation import Simulation
from morpheus.simulation.options import (
    ConformerSearchMethod,
    ConformerSearchOptions,
    GFNLevel,
    SimulationOptions,
    Solvent,
)
from morpheus.molecule.smiles import Smiles
from morpheus.utils.units import EnergyUnit, convert

co2_addition = ReactionTemplate(
    r"[#6-;v3;D2:1]~1~[#7+;v4:2]~[$([#6;v4]),$([#7;v3]):3]~[$([#6;v4;X3]),$([#7;v3;X2]):4]~[$([#7;v3]),$([#16;v2]):5]1>>[#6+0;v4;X3:1](C(=O)[O-])-1=[#7+;v4;X3:2]-[$([#6;v4;X3]),$([#7;v3;X2]):3]=[$([#6;v4;X3]),$([#7;v3;X2]):4]-[$([#7;v3]),$([#16;v2]):5]1"
)

options = SimulationOptions(
    gfn_level=GFNLevel.GFN2,
    xtb_cores=12,
    solvent=Solvent.DMSO,
    conformer_search_options=ConformerSearchOptions(
        method=ConformerSearchMethod.RDKIT,
        rdkit_level=200,
        crest_level=GFNLevel.GFN0,
    ),
)

simulation = Simulation(options)

co2 = Molecule(Smiles(r"O=C=O"))
co2_delta_g = simulation.calculate_delta_g(co2)

substrate = Smiles(r"[C-]1N(C)C=C[N+](C)=1")

reaction = Reaction(co2_addition)
reaction.add_reactants([substrate])
reaction.run_reaction()
dg = simulation.calculate_delta_g(reaction.products[0]) - co2_delta_g
print(convert(dg, EnergyUnit.Eh, EnergyUnit.kJMol))
