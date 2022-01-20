from x2df import x2df
from x2df.examples import examples
import sys
import pytest

trace = str(sys.gettrace())
debuggerAttached = not trace.startswith("<coverage.")
pytestmark = pytest.mark.skipif(
    not debuggerAttached,
    reason="These tests are debug-hooks and will be skipped during normal tests",
)


def test_csvParsingGui(tmp_path):
    exampleDict = examples.getClassDict()
    e = "stepresponses1"
    dfout = exampleDict[e]().createDF()
    dst = tmp_path / f"{e}.csv"
    dfout.attrs["parseinfo"] = {"sep": "-"}
    open(dst, "w").write(x2df.dump(dfout, "csv"))
    # we dump the df, then remove the parseinfo.
    # this way, the parser will fail at first.
    lines = [x for x in open(dst, "r").readlines() if not x.startswith("#")]
    open(dst, "w").writelines(lines)
    dfsin = x2df.load(dst)
    assert dfsin
