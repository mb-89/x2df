from x2df.fileIOhandlers import fileIOhandlers
from x2df import x2df
from x2df.examples import examples
from x2df.fileIOhandlers.fileIOhandler_csv import (
    ParserDialog,
    readCSV,
    peekCSV,
    updateOrigParseInfo,
)
from pyqtgraph import mkQApp, QtCore

handlerDict = fileIOhandlers.getClassDict()


def test_knownCSVformat(tmp_path):
    exampleDict = examples.getClassDict()
    e = "stepresponses1"
    dfout = exampleDict[e]().createDF()
    dst = tmp_path / f"{e}.csv"
    open(dst, "w").write(x2df.dump(dfout, "csv"))
    dfsin = x2df.load(dst, postprocess=False)
    assert len(dfsin[0]) == len(dfout)
    assert all(dfout.columns == dfsin[0].columns)
    # check the path with postprocessing:
    dfsin = x2df.load(dst, postprocess=True)


def test_unknownCSVformat(qtbot, tmp_path):
    exampleDict = examples.getClassDict()
    e = "stepresponses1"
    dfout = exampleDict[e]().createDF()
    dst = tmp_path / f"{e}.csv"
    dfout.attrs["parseinfo"] = {"sep": ";"}
    open(dst, "w").write(x2df.dump(dfout, "csv"))
    # we dump the df, then remove the parseinfo.
    # this way, the parser will fail at first.
    lines = [x for x in open(dst, "r").readlines() if not x.startswith("#")]
    open(dst, "w").writelines(lines)

    _ = mkQApp()
    dlg = ParserDialog(dst)
    qtbot.addWidget(dlg)
    dlg.show()
    blocker = qtbot.waitSignal(dlg.readySig)
    blocker.wait()
    assert not dlg.apply.isEnabled()
    dlg.cfgItems["sep"].setText('";"')
    dlg.parse()
    assert dlg.result["sep"] == ";"
    assert dlg.apply.isEnabled()
    qtbot.mouseClick(dlg.apply, QtCore.Qt.LeftButton)


def test_unknownCSVformatTriggersGUI(qtbot, tmp_path):
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

    def closeDlg():
        app = mkQApp()
        dlg = app.topLevelWidgets()[0]
        dlg.reject()

    QtCore.QTimer.singleShot(0, closeDlg)
    dfsin = x2df.load(dst, postprocess=False)
    assert dfsin[0].empty


def test_invalidCSVformatTriggersGUI(qtbot, tmp_path):
    exampleDict = examples.getClassDict()
    e = "stepresponses1"
    dfout = exampleDict[e]().createDF()
    dst = tmp_path / f"{e}.csv"
    dfout.attrs["parseinfo"] = {"sep": "-"}
    open(dst, "w").write(x2df.dump(dfout, "csv"))
    # we dump the df, then invalidate the parseinfo.
    # this way, the parser will fail at first.
    lines = [x for x in open(dst, "r").readlines() if not x.startswith("#")]
    lines = ['#{"parseinfo":{"sep":";"}}\n'] + lines
    open(dst, "w").writelines(lines)

    def closeDlg():
        app = mkQApp()
        w = app.topLevelWidgets()
        assert w
        dlg = w[0]
        dlg.reject()

    QtCore.QTimer.singleShot(0, closeDlg)
    dfsin = x2df.load(dst, postprocess=False)
    assert dfsin[0].empty


def test_parsingException(tmp_path):
    dst = tmp_path / "doesntExist.csv"
    df = readCSV(dst, {})
    assert df.empty


def test_peekException(tmp_path):
    dst = tmp_path / "doesntExist.csv"
    df = peekCSV(dst, {})
    assert df.empty


def test_cfgjsonSyntaxErr(qtbot, tmp_path):
    exampleDict = examples.getClassDict()
    e = "stepresponses1"
    dfout = exampleDict[e]().createDF()
    dst = tmp_path / f"{e}.csv"
    open(dst, "w").write(x2df.dump(dfout, "csv"))
    txt = open(dst, "r").read()
    txt = txt.replace('"comment":', "INVALIDSYNTAX")
    open(dst, "w").write(txt)

    def closeDlg():
        app = mkQApp()
        dlg = app.topLevelWidgets()[0]
        dlg.reject()

    QtCore.QTimer.singleShot(0, closeDlg)
    dfsin = x2df.load(dst, postprocess=False)
    assert dfsin[0].empty


def test_updateParseInfo(qtbot, tmp_path):
    exampleDict = examples.getClassDict()
    e = "stepresponses1"
    dfout = exampleDict[e]().createDF()
    dst = tmp_path / f"{e}.csv"
    open(dst, "w").write(x2df.dump(dfout, "csv"))

    def AnswerNo():
        app = mkQApp()
        dlg = app.topLevelWidgets()[0]
        dlg.reject()

    QtCore.QTimer.singleShot(50, AnswerNo)
    updateOrigParseInfo(dst, {}, {"comment": '"#"'}, True)

    qtbot.wait(100)
    open(dst, "w").write(x2df.dump(dfout, "csv"))

    def AnswerYes():
        app = mkQApp()
        dlg = app.topLevelWidgets()[0]
        dlg.accept()

    QtCore.QTimer.singleShot(50, AnswerYes)
    updateOrigParseInfo(dst, {}, {"comment": '"#"'}, True)
    assert open(dst, "r").readline().startswith("#{")
