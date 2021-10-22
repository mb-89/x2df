import logging
import argparse
from .__metadata__ import __version__
from x2df.fileIOhandlers import fileIOhandlers
from x2df.examples import examples
from glob import glob
import os.path as op
import shutil
import tempfile
import py7zr

log = logging.getLogger("x2df")

# https://stackoverflow.com/a/59305379
try:
    shutil.register_unpack_format("7zip", [".7z"], py7zr.unpack_7zarchive)
except shutil.RegistryError:  # pragma: no cover
    pass
try:
    shutil.register_archive_format("7zip", py7zr.pack_7zarchive)
except shutil.RegistryError:  # pragma: no cover
    pass


def main(argv):
    parser = argparse.ArgumentParser(
        "parses given glob-style paths and extracts dataframes."
        + " Dumps all dataframes into the dst directory"
    )
    parser.add_argument("srcs", nargs="*", help="glob-style paths that will be parsed")
    parser.add_argument("dst", nargs="?", help="destination path for the results.")
    parser.add_argument(
        "--dstfmt",
        choices=sorted(list(fileIOhandlers.getClassDict().keys())),
        help="data format for the results. Defaults to parquet.",
        default="parquet",
    )
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

    # if we are here, we have srcs and a have a dst.
    # it makes no sense to call the cmd line utility without a dst.
    for src in args["srcs"]:
        dfs = load(src)
        for df in dfs:
            dump(df, args["dst"], args["dstfmt"])
    return 0


def getExampleNames():
    return tuple(sorted(("example_" + x for x in examples.getClassDict().keys())))


def load(src, postprocess=True, _claimedPaths=[]):
    src = str(src)
    globresults = glob(src)
    # gate #1: check if we want to load an example
    if not globresults:
        if src.startswith("example_"):
            return examples.loadExample(src)
        else:
            return []

    # gate #2: check if we have more than one result
    if len(globresults) > 1:
        dfList = []
        files = [x for x in globresults if op.isfile(x)]
        dirs = [x for x in globresults if op.isdir(x)]
        for x in files:
            dfList.extend(load(x, postprocess=postprocess, _claimedPaths=_claimedPaths))
        for x in dirs:
            # we check the files before the dirs, because with some formats,
            # a file can claim adjacent dirs
            dfList.extend(load(x, postprocess=postprocess, _claimedPaths=_claimedPaths))
        return dfList

    x = globresults[0]

    # gate #3: check if the given path is already claimed
    if x in _claimedPaths:
        return []

    # gate #4: check if the given path is a dir, and if so, glob it
    if op.isdir(x):
        return load(src + "/*", postprocess=postprocess, _claimedPaths=_claimedPaths)

    # finally, if we are here, x is the path of a single file.
    # Now we can check if any of the installed parsers claims it
    for name, hdl in fileIOhandlers.getClassDict().items():
        claims = hdl().claim(x)
        if not claims:
            continue
        _claimedPaths.extend(claims)
        dfs = hdl().parse(x, postprocess=postprocess)
        return dfs

    # if None of the handlers claimed the file, check if it is an archive.
    # if so, extract and treat like a folder
    with tempfile.TemporaryDirectory() as td:
        try:
            shutil.unpack_archive(x, td)
            return load(td + "/*", postprocess=postprocess, _claimedPaths=_claimedPaths)
        except (ValueError, shutil.ReadError) as _:  # noqa: F841
            return []  # if we are here, we found nothing


def dump(df, dst, fmt):
    fileIOhandlers.getClassDict()[fmt]().dump(df, dst)
