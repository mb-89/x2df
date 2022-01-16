from x2df.examples import examples
from x2df import x2df


def test_dumpWithoutDst(tmp_path):
    exampleDict = examples.getClassDict()
    e = "stepresponses1"
    dfout = exampleDict[e]().createDF()
    assert x2df.dump(dfout, "parquet") is None
