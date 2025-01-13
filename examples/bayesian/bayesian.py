from GPyOpt.methods import BayesianOptimization

from morpheus.molecule import Smiles, Molecule
from morpheus.reaction import ReactionTemplate, Reaction
from morpheus.simulation import Simulation
from morpheus.simulation.options import (
    SimulationOptions,
    ConformerSearchOptions,
    ConformerSearchMethod,
    GFNLevel,
    Solvent,
)

smiles_file = open("examples/bayesian/data/nhc.smiles", "r")

smiles_list = []
for line in smiles_file:
    try:
        smiles_list.append(Smiles(line))
    except:
      pass

bounds = [{"name": "index", "type": "continuous", "domain": (0, len(smiles_list) - 1)}]


co2_addition = ReactionTemplate(
    r"[#6-;v3;D2:1]~1~[#7+;v4:2]~[$([#6;v4]),$([#7;v3]):3]~[$([#6;v4;X3]),$([#7;v3;X2]):4]~[$([#7;v3]),$([#16;v2]):5]1>>[#6+0;v4;X3:1](C(=O)[O-])-1=[#7+;v4;X3:2]-[$([#6;v4;X3]),$([#7;v3;X2]):3]=[$([#6;v4;X3]),$([#7;v3;X2]):4]-[$([#7;v3]),$([#16;v2]):5]1"
)

options = SimulationOptions(
    gfn_level=GFNLevel.GFN0,
    xtb_cores=12,
    solvent=Solvent.DMSO,
    conformer_search_options=ConformerSearchOptions(
        method=ConformerSearchMethod.RDKIT, rdkit_level=200
    ),
)

simulation = Simulation(options)

co2 = Molecule(Smiles("O=C=O"))
delta_g_co2 = simulation.calculate_delta_g(co2)

def objective(params) -> float:
    i = int(params[0][0])
    r = Reaction(co2_addition)
    r.add_reactants([smiles_list[i]])
    r.run_reaction()
    if r.products:
        delta_g = simulation.calculate_delta_g(r.products[0])-delta_g_co2
        return delta_g
    return 2**308


optimizer = BayesianOptimization(
    f=objective, domain=bounds, model_type="GP", initial_design_numdata=5
)
optimizer.run_optimization(max_iter=int(len(smiles_list)/10))

print(optimizer.x_opt)
print(smiles_list[int(optimizer.x_opt[0])])
print(optimizer.fx_opt)

print(len(optimizer.get_evaluations()))