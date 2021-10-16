from x2df import x2df
import tempfile
import pathlib
from x2df.dumpers import dumpers
from x2df.examples import examples
import itertools

dumperDict = dumpers.getClassDict()
exampleDict = examples.getClassDict()


def test_create_dump_parse_examples(tmp_path):
    # in this test, we iterate over all examples and dumpers,
    # dump the data and parse it back.
    combis = [(i, j) for i, j in zip(exampleDict, itertools.cycle(dumperDict))]
    del combis  # only to please flake


def test_parse_dump_via_main(tmp_path):
    # here, we use the main fcn to parse and dump one file (for coverage)
    ex = list(exampleDict.keys())[0]
    dump = list(dumperDict.keys())[0]
    dst = str(tmp_path / (ex + f".{dump}"))
    assert x2df.main(["test", f"example_{ex}", dst, "--dstfmt", dump]) == 0


if __name__ == "__main__":
    dst = tempfile.TemporaryDirectory()
    test_create_dump_parse_examples(pathlib.Path(dst.name))
    test_parse_dump_via_main(pathlib.Path(dst.name))
