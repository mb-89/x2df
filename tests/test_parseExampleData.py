from x2df import x2df
import pytest
import os.path as op
from . import examples

exampleList = examples.getExampleNameList() + ["invalidExampleName"]


@pytest.mark.parametrize("exampleDataFilePaths", exampleList, indirect=True)
def test_parsingExampleData(exampleDataFilePaths):
    src = exampleDataFilePaths
    if not src:
        return
    dst = op.join(op.dirname(src), op.splitext(op.basename(src))[0] + "_dfs.parquet")
    assert x2df.main(["test", str(src), str(dst)]) == 0
