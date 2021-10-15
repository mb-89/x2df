import logging
import argparse
from .__metadata__ import __version__

log = logging.getLogger("x2df")


def main(argv):
    parser = argparse.ArgumentParser(
        "parses given glob-style paths and extracts dataframes"
    )
    parser.add_argument("srcs", nargs="*", help="glob-style paths that will be parsed")
    parser.add_argument("dst", nargs="?", help="destination path for the results")
    parser.add_argument(
        "-?", action="store_true", help="show this help message and exit"
    )
    parser.add_argument("-v", "--version", action="store_true", help="prints version")
    args = argv[1:]
    args = vars(parser.parse_args(args))
    if len(args["srcs"]) > 1:
        args["dst"] = args["srcs"].pop(-1)

    if args["version"]:
        print(__version__)
        return 0
    if args["?"] or not args["srcs"] or not args["dst"]:
        parser.print_help()
        return 0

    # if we are here, we have srcs and a dst
    log.info(args)
    return 0
