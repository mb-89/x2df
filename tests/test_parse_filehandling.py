import pytest
import os
import os.path as op
from pandas import DataFrame
from x2df.fileIOhandlers import fileIOhandlers
from x2df.fileIOhandlers.__fileIOhandler__ import FileIOhandler as FIObaseclass
from x2df import x2df
import shutil

handlerDict = fileIOhandlers.getClassDict()


def test_parse_invalid_and_directory(tmp_path):
    # create a file that will never be a valid measurement and try to parse it
    # also create some folders and subfolders to test the subfolder resolving mechanism
    invalidpath = tmp_path / "subdir"
    os.makedirs(invalidpath / "subsubdir")
    dfs = x2df.load(invalidpath)
    assert dfs == []

    open(invalidpath / "invalidfile1", "w").write("This file is invalid")
    open(invalidpath / "invalidfile2", "w").write("This file is invalid")
    open(invalidpath / "subsubdir/invalidfile3", "w").write("This file is invalid")

    dfs = x2df.load(invalidpath)
    dfs = x2df.load(invalidpath / "subsubdir")
    assert dfs == []

    dfs = x2df.load(invalidpath / "bla")  # non-existing file
    assert dfs == []


def test_claimed_file(tmp_path, monkeypatch):
    # we dont support a format that claimes other files yet, so lets design a mockup:
    class ClaimingFileIO(FIObaseclass):
        def claim(self, path):
            dirname = op.dirname(path)
            basename = op.splitext(op.basename(path))[0]

            m = op.join(dirname, basename + ".claim_master")
            s = op.join(dirname, basename + ".claim_slave")

            if not op.isfile(m):
                return []
            if not op.isfile(s):
                return []

            return [m, s]  # we claim both files if we find both

        def parse(self, path, postprocess=True):
            res = [DataFrame()]
            return res

    # monkey-path the new class into the existing classes
    tempHandlers = dict((k, v) for k, v in handlerDict.items())
    tempHandlers["claim"] = ClaimingFileIO

    def tmpfn():
        return tempHandlers

    monkeypatch.setattr(fileIOhandlers, "getClassDict", tmpfn)

    # now if we call the load-function, it will be able to load ".claim_..." files
    # and return an empty dataframe

    open(tmp_path / "file.claim_master", "w").write("")
    open(tmp_path / "file.claim_slave", "w").write("")

    dfs = x2df.load(tmp_path)
    assert len(dfs) == 1
    assert dfs[0].empty


def test_unimplementedIOHandler():  # check the notimpl functions of the baseclass
    FIObase = FIObaseclass()
    with pytest.raises(NotImplementedError):
        FIObase.parse("anypath")
    with pytest.raises(NotImplementedError):
        FIObase.dump("anydf", "anypath")
    with pytest.raises(NotImplementedError):
        FIObase.claim("anypath")


def test_archives(tmp_path):  # for coverage of the archive unzipper path
    os.makedirs(tmp_path / "arch")
    x2df.dump(DataFrame(), "parquet", tmp_path / "arch" / "emptydf.parquet")
    shutil.make_archive(tmp_path / "archfile.7z", "7zip", root_dir=tmp_path / "arch")
    shutil.rmtree(tmp_path / "arch")
    dfs = x2df.load(tmp_path)
    assert len(dfs) == 1
