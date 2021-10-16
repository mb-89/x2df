from x2df import x2df
from x2df.examples import examples
import itertools
from x2df.fileIOhandlers import fileIOhandlers

handlerDict = fileIOhandlers.getClassDict()
exampleDict = examples.getClassDict()


def test_create_dump_parse_examples(tmp_path):
    # in this test, we iterate over all examples and dumpers,
    # dump the data and parse it back.
    files = []
    if len(exampleDict) > len(handlerDict):
        combis = [(i, j) for i, j in zip(exampleDict, itertools.cycle(handlerDict))]
    else:
        combis = [(i, j) for i, j in zip(itertools.cycle(exampleDict), handlerDict)]

    # dump the dataframes to all known formats
    for e, d in combis:
        df = exampleDict[e]().createDF()
        dst = tmp_path / f"{e}.{d}"
        x2df.dump(df, dst, d)
        files.append((dst, df))

    # read the dumps back and assert equality (must only hold when not postprocessing)
    for f, origdf in files:
        dfs = x2df.load(f, postprocess=False)
        assert dfs[0].equals(origdf)


def test_parse_dump_via_main(tmp_path):
    # here, we use the main fcn to parse and dump one file (for coverage)
    ex = list(exampleDict.keys())[0]
    dump = list(handlerDict.keys())[0]
    dst = str(tmp_path / (ex + f".{dump}"))
    assert x2df.main(["test", f"example_{ex}", dst, "--dstfmt", dump]) == 0
