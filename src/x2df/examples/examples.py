from glob import glob
import os.path as op
from functools import cache
from x2df.fileIOhandlers.__fileIOhandler__ import FileIOhandler


@cache
def getClassDict():
    prefix = "example_"
    classes = {}
    mods = glob(op.join(op.dirname(__file__), "*.py"))
    mods = [f for f in mods if op.isfile(f) and op.basename(f).startswith(prefix)]
    mods = [(op.splitext(op.basename(f))[0], f) for f in mods]
    for (
        mname,
        mfile,
    ) in mods:  # this is ugly, but otherwise the coverage report doesnt find it...
        importname = f"x2df.examples.{mname}"
        exec("import " + importname)
        classes[mname.replace(prefix, "")] = eval(f"{importname}.Example")
    return classes


@cache
def loadExample(examplename):
    dfs = []
    examplename = examplename.replace("example_", "")
    dct = getClassDict()
    if examplename == "all":
        exs = dct.values()
    else:
        exs = [dct.get(examplename)]
    for ex in exs:
        dfs.extend(FileIOhandler().processRawDF(ex().createDF()))
    return dfs
