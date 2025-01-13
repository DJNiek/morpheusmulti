from pathlib import Path
from typing import Callable
import threading
import os
import sys

from morpheus.cli.parser import parser
from morpheus.cli.helper import chunk_into_n, flatten, get_combinations

from morpheus.reaction import Reaction

from morpheus.simulation import Simulation, SimulationOptions

from morpheus.utils.information import MORPHEUS
from morpheus.utils.units import EnergyUnit, EnergyValue
from morpheus.cli.output import Output

from morpheus.cli.fancy_prints import (
    log,
    result,
    error,
    command,
    subscript_number,
    list_obj,
    bold,
    plain,
)

import sys


class Logger(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        sys.__stdout__.flush()
        sys.__stdout__.write(obj)
        for f in self.files:
            f.write(plain(obj))
            f.flush()

    def flush(self):
        sys.__stdout__.flush()
        for f in self.files:
            f.flush()

def main():
    logger = Logger()

    def start_thread(*args) -> threading.Thread:
        thread = threading.Thread(target=process_chunk, args=args)
        thread.start()
        return thread

    def process_chunk(
        thread_idx, chunk: list[list[int]], running_idx, write: Callable[[float], None]
    ):
        for idx, indices in enumerate(chunk):
            reactants = []
            for i, index in enumerate(indices):
                reactants.append(parsed_options.reactants[i][index])
            reaction_idx = running_idx + 1 + idx

            reaction = Reaction(parsed_options.reaction)
            reaction.add_reactants(reactants)
            reaction.run_reaction()

            p = reaction.products[0] if reaction.products else None
            prods = reaction.products[0].products if p else None

            out = bold(
                " . ".join(map(lambda prod: f"{prod}", prods or [])),
                "green" if prods else "red",
            )
            list_obj(reaction_idx, f"{' . '.join(reactants)} >> {out}")
            del prods

            if p:
                reaction_num = bold(reaction_idx, "blue")
                log(f"Calculating ΔG for reaction {reaction_num}...")

                delta_g = EnergyValue(
                    simulation.calculate_delta_g(reaction.products[0]),
                    EnergyUnit.Eh,
                )

                delta_g_print = bold(delta_g.to(EnergyUnit.kJMol), color="magenta")

                result(
                    f"ΔG{bold(subscript_number(reaction_idx), color='yellow')} = {delta_g_print}"
                )

                output.add_reaction(p.reactants, p.products, delta_g)

                try:
                    write(thread_idx, delta_g.to(EnergyUnit.kCalMol).value)
                except:
                    error(f"Error, tried to write to {thread_idx}")

    def write(thread_idx, data):
        thread_summary[thread_idx].append(data)

    # ensure that `morpheus` can be found in scope
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # construct morpheus.cli.ParserOptions object
    parsed_options = parser.parse()

    options = SimulationOptions(
        gfn_level=parsed_options.xtb_gfn,
        xtb_cores=parsed_options.xtb_cores,
        conformer_search_options=parsed_options.conformer_search,
        solvent=parsed_options.solvent,
    )

    simulation = Simulation(options)

    output = Output(options)

    if parsed_options.output_path:
        outfile = open(parsed_options.output_path, "w+")
        logger.files = (*logger.files, outfile)
        outfile.write(MORPHEUS)
        outfile.write("\n")
        outfile.write("\n")
        outfile.write(output.generate_options())
        outfile.flush()

    sys.stdout = logger
    
    log(f"Processing on {bold(parsed_options.cores, 'blue')} cores. ")
    log(
        f"Allocating {bold(parsed_options.xtb_cores, 'blue')} parallel processors to xtb"
    )

    reactions = get_combinations(
        list(map(lambda reactants: len(reactants), parsed_options.reactants))
    )

    num_reactions = bold(len(reactions), "yellow")
    command(f"Running a total of {num_reactions} reactions: ")
    del num_reactions

    if options.solvent:
        log(f"using implicit solvent model {bold(options.solvent.value, 'blue')}")

    # split workload
    chunks = chunk_into_n(reactions, parsed_options.cores)

    # output of the different threads
    thread_summary = [[] for _ in range(parsed_options.cores)]

    # empty array of threads
    threads = [None for _ in range(parsed_options.cores)]

    # keep the index of the first reaction each thread processes
    running_idx = 0
    for i in range(parsed_options.cores):
        chunk = chunks[i]
        threads[i] = start_thread(i, chunk, running_idx, write)
        running_idx += len(chunk)

    for t in threads:
        t.join()

    # flatten
    delta_gs = flatten(thread_summary)

    output.generate_table()
    for f in parsed_options.output_formats:
        if not parsed_options.output_path == None:
            print(parsed_options.output_path)
            data_filename = Path(f"{parsed_options.output_path}.{f.value}")
            with open(data_filename, "w+") as data_file:
                log(f"wrote data to file {bold(data_filename, 'blue')}")
                data_file.write(output.data_as(f))
        else:
            log(f"data as {bold(f.name, 'blue')}")
            print(output.data_as(f))

    if parsed_options.output_path:
        outfile = open(parsed_options.output_path, "a+")
        outfile.write("\n")
        outfile.write("\n")
        outfile.write(output.stdout)

if __name__ == "__main__":
    main()
