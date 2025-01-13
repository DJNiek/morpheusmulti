from morpheus.molecule import Smiles
from morpheus.reaction import ReactionTemplate, Reaction
from morpheus.simulation import Simulation, SimulationOptions
from morpheus.simulation.options import (
    ConformerSearchMethod,
    ConformerSearchOptions,
    GFNLevel,
)

oxy_cope = ReactionTemplate(
    r"[#6:1]=[#6:2]-[#6:3]-[#6:4]([#8])[#6:5]=[#6:6]>>[#6:3]=[#6:2]-[#6:1]-[#6:6]-[#6:5]-[#6:4]=[#8]"
)

options = SimulationOptions(
    gfn_level=GFNLevel.GFN2,
    xtb_cores=12,
    conformer_search_options=ConformerSearchOptions(
        method=ConformerSearchMethod.RDKIT,
        rdkit_level=200,
    ),
)

simulation = Simulation(options)

substrate = Smiles(r"C(O)(C=C)1CC2CCC1C=C2")

reaction = Reaction(oxy_cope)
reaction.add_reactants([substrate])
reaction.run_reaction()

print(reaction.products[0])

delta_g = simulation.calculate_delta_g(reaction.products[0])

print(reaction.products[0])

print(f"Delta G in Eh {delta_g}")