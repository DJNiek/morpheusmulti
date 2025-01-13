import argparse
import os
import shutil
import sys
from pathlib import Path

from morpheus.cli.fancy_prints import log, error, bold
from morpheus.cli.parser import ParserOptions
from morpheus.cli.parser.options import FileFormat
from morpheus.molecule.smiles import Smiles
from morpheus.simulation.options import (
    ConformerSearchMethod,
    ConformerSearchOptions,
    GFNLevel,
    Solvent,
)
from morpheus.utils.information import TMP_DIR
from morpheus.reaction import ReactionTemplate


class MorpheusParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.exit(2)


# TODO: add options SMARTSFILE -sf
# TODO: improve input files (multiple reactants)


def get_parser():
    # parse command line arguments
    parser = MorpheusParser(
        prog="morpheus",
        description="calculate the gibbs free energy for any SMARTS reaction ",
    )
    parser.add_argument(
        "-s",
        "--smiles",
        type=str,
        nargs="+",
        required=False,
        help="smiles of the reactants",
    )
    parser.add_argument(
        "-sf",
        "--smiles-files",
        help="input files of the reactants SMILES",
        nargs="+",
        required=False,
    )
    parser.add_argument(
        "-cs", "--conformer-search", action="store_true", help="search for conformers"
    )
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument(
        "-csm",
        "--conformer-search-method",
        help="Method to use for conformer searching [rdkit, crest]",
    )
    parser.add_argument(
        "-csl",
        "--conformer-search-level",
        help="for rdkit number of conformers searched, for crest {gfnff, gfn0, gfn1, gfn2}",
    )
    parser.add_argument(
        "-gfn", type=str, choices=["0", "1", "2"], help="Level of gfn", default="2"
    )
    parser.add_argument(
        "-p", "--processors", help="number of cores to use", type=int, default=1
    )
    parser.add_argument(
        "-xtbc",
        "--xtb-cores",
        help="number of cores to use for xtb",
        type=int,
        default=os.cpu_count(),
    )
    parser.add_argument(
        "-xtba",
        "--xtb-auto",
        help="automatically choose the number of cores for xtb, based on available processors",
        action="store_true",
    )
    parser.add_argument(
        "-S",
        "--smarts",
        help="smarts of the reaction to run",
        default=r"[#6-;v3;D2:1]~1~[#7+;v4:2]~[$([#6;v4]),$([#7;v3]):3]~[$([#6;v4;X3]),$([#7;v3;X2]):4]~[$([#7;v3]),$([#16;v2]):5]1>>[#6+0;v4;X3:1](C(=O)[O-])-1=[#7+;v4;X3:2]-[$([#6;v4;X3]),$([#7;v3;X2]):3]=[$([#6;v4;X3]),$([#7;v3;X2]):4]-[$([#7;v3]),$([#16;v2]):5]1",
    )

    parser.add_argument(
        "-rt",
        "--reaction-type",
        help="select if you want to run the reaction for each pair of reactants or for any combination of given reactants",
        default="cross",
        choices=["cross", "separate"],
    )

    parser.add_argument(
        "-f",
        "--formats",
        nargs="+",
        help="format output file",
        choices=["json", "csv"],
        required=False,
    )

    parser.add_argument(
        "--solvent",
        help="solvent to add to the xtb command (using -alpb)",
        required=False,
        choices=Solvent.solvents(),
    )

    return parser


def get_options(args) -> ParserOptions:
    arg_smiles = args.smiles or []
    output_path = Path(args.output) if args.output else None
    do_conformer_search = args.conformer_search
    cs_method = args.conformer_search_method
    cs_level = args.conformer_search_level
    cores = args.processors
    xtb_gfn_arg = args.gfn
    xtb_cores = args.xtb_cores if not args.xtb_auto else os.cpu_count() // cores
    xtb_cores = 1 if xtb_cores == 0 else xtb_cores
    reaction = ReactionTemplate(args.smarts)
    output_formats = list(map(lambda f: FileFormat.from_string(f), args.formats or []))
    solvent = Solvent.from_string(args.solvent)

    cs_options = None
    if do_conformer_search:
        cs_options = ConformerSearchOptions()
        if not cs_method:
            log(
                f"No conformer search method specified, using default [{bold('rdkit', color='blue')}]"
            )
        else:
            if cs_method == "rdkit":
                log(f"Performing conformer search using [{bold('rdkit', 'blue')}]")
                cs_options.method = ConformerSearchMethod.RDKIT
                cs_options.accuracy = cs_level or 200
            elif cs_method == "crest":
                log(f"Performing conformer search using [{bold('crest', 'blue')}]")
                cs_options.method = ConformerSearchMethod.CREST
                gfn_level = None
                match cs_level:
                    case "gfnff":
                        gfn_level = GFNLevel.GFNFF
                    case "gfn0":
                        gfn_level = GFNLevel.GFN0
                    case "gfn1":
                        gfn_level = GFNLevel.GFN1
                    case "gfn2":
                        gfn_level = GFNLevel.GFN2
                cs_options.accuracy = gfn_level or GFNLevel.GFN0
            else:
                error(f"Unknown conformer search method: [{bold(cs_method, 'red')}]")
                exit(-1)

    # check if all arg_smiles are valid
    for idx, smile in enumerate(arg_smiles):
        try:
            arg_smiles[idx] = Smiles(smile)
        except:
            error(f"Command line input {bold(smile, 'red')} is not a valid SMILES")
            exit(-1)

    # log number of smiles and reactions
    arg_smiles_len = bold(len(arg_smiles), "blue")

    cmd_invocation = bold("command invocation", "blue")
    log(f"Reading {arg_smiles_len} SMILES from {cmd_invocation}...")
    del cmd_invocation

    xtb_gfn = GFNLevel.GFN2
    match xtb_gfn_arg:
        case 0:
            xtb_gfn = GFNLevel.GFN0
        case 1:
            xtb_gfn = GFNLevel.GFN1
        case 2:
            xtb_gfn = GFNLevel.GFN2

    def get_smiles(filename: str | None):
        if filename:
            return open(Path(filename), "r").read().splitlines()
        return []

    reactants = [[] for _ in range(max(len(args.smiles_files or []), len(arg_smiles)))]

    for i, _ in enumerate(reactants):
        reactants[i] += list(
            map(
                lambda smiles: Smiles(smiles),
                get_smiles(
                    (
                        args.smiles_files
                        or [None for _ in range(reaction.get_num_reactants())]
                    )[i]
                ),
            )
        )

    for i in range(len(arg_smiles)):
        reactants[i].append(arg_smiles[i])

    if not len(reactants) == reaction.get_num_reactants():
        error(
            f"Reactants given did not match the SMARTS, expected {bold(reaction.get_num_reactants(), 'red')} but got {bold(len(reactants), 'red')}"
        )
        exit(-1)

    return ParserOptions(
        output_path=output_path,
        xtb_gfn=xtb_gfn,
        conformer_search=cs_options or None,
        cores=cores,
        xtb_cores=xtb_cores,
        reaction=reaction,
        reactants=reactants,
        output_formats=output_formats,
        solvent=solvent,
    )


def cleanup(_parser):
    log("executing cleanup...")
    shutil.rmtree(TMP_DIR)
    os.mkdir(TMP_DIR)
    exit(0)


def display_help(parser):
    parser.print_help()
    exit(0)


def parse() -> ParserOptions:
    parser = get_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)
    subparsers = parser.add_subparsers(dest="subcmd", help="Utility commands")
    parser_cleanup = subparsers.add_parser("clean", help="remove all tmp files")
    parser_help = subparsers.add_parser("help", help="display this help menu")
    parser_help.set_defaults(func=display_help)
    parser_cleanup.set_defaults(func=cleanup)
    args = parser.parse_args()
    if args.subcmd:
        args.func(parser)
    return get_options(args)
