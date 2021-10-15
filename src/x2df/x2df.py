import logging
import argparse
from .__metadata__ import __version__

log = logging.getLogger("x2df")


def main(argv):
    parser = argparse.ArgumentParser(
        "parses given glob-style paths and extracts dataframes"
    )
    parser.add_argument("paths", nargs="*")
    parser.add_argument(
        "-?", action="store_true", help="show this help message and exit"
    )
    parser.add_argument("-v", "--version", action="store_true", help="prints version")
    args = argv[1:]
    args = vars(parser.parse_args(args))
    if args["version"]:
        print(__version__)
        return
    if args["?"] or not args["paths"]:
        parser.print_help()
        return 0
    log.info(args)
    return 0
