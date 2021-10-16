from glob import glob
import os.path as op
from functools import cache


@cache
def getClassDict():
    prefix = "dumper_"
    classes = {}
    mods = glob(op.join(op.dirname(__file__), "*.py"))
    mods = [f for f in mods if op.isfile(f) and op.basename(f).startswith(prefix)]
    mods = [(op.splitext(op.basename(f))[0], f) for f in mods]
    for (
        mname,
        mfile,
    ) in mods:  # this is ugly, but otherwise the coverage report doesnt find it...
        importname = f"x2df.dumpers.{mname}"
        exec("import " + importname)
        classes[mname.replace(prefix, "")] = eval(f"{importname}.Dumper")
    return classes
