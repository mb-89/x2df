from x2df.fileIOhandlers.__fileIOhandler__ import FileIOhandler
from pandas import DataFrame, read_csv
import json
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import io
import inspect

# we want to do the imports as late as possible to
# keep it snappy once we have more and more fileIOhandlers

dumpparams = inspect.signature(DataFrame.to_csv).parameters.keys()


class Handler(FileIOhandler):
    def dump(self, df, dst=None, **kwargs):
        kwargs["index"] = False
        kwargs["line_terminator"] = "\n"
        parseinfo = df.attrs.setdefault("parseinfo", {})
        parseinfo["comment"] = "#"
        metastr = "#" + json.dumps(df.attrs, indent=4).replace("\n", "\n#") + "\n"
        allargs = kwargs | parseinfo
        allargs = dict((k, v) for k, v in allargs.items() if k in dumpparams)
        csvstring = metastr + df.to_csv(**allargs)
        if dst is not None:
            open(dst, "w").write(csvstring)
            return None
        return csvstring

    def parse(self, path, postprocess=True):
        # since csvs are not a well-defined format, lets try a few things:
        # first, check if the file starts with a metadata comment,
        #  we take the parser args from there
        with open(path, "r") as f:
            origmetadata = getMetadata(f)
        skip = False
        dfraw = DataFrame()
        while not skip:
            parseinfo, infoValid = getParseInfo(path)
            if not infoValid:
                break
            dfraw = readCSV(path, parseinfo)
            skip |= not dfraw.empty

        # if the parsing was successfull and we changed the original metadata,
        # ask if we should add the metadata to the top of the file.
        updateOrigParseInfo(path, origmetadata, parseinfo, not dfraw.empty)

        if postprocess:
            return self.processRawDF(dfraw)
        else:
            return [dfraw]

    def claim(self, path):
        if path.endswith(".csv"):
            return [path]
        else:
            return []


def readCSV(path, parseInfo):
    dfraw = DataFrame()
    try:
        dfraw = read_csv(path, **parseInfo)
    except Exception:
        pass
    # we make an assumption here: if we only have one column,
    # then it is likely that the parsing was incorrect (bc of invalid separator).
    # In that case, we dont accept the result
    if len(dfraw.columns) < 2:
        parseInfo.clear()
        dfraw = DataFrame()
    return dfraw


def updateOrigParseInfo(path, origmetadata, newparseinfo, isValid):
    if not isValid or origmetadata.get("parseinfo") == newparseinfo:
        return
    msgbox = QtWidgets.QMessageBox()
    msgbox.setWindowTitle("csv parsing")
    msgbox.setText("CSV parse info was changed")
    msgbox.setInformativeText(f"Do you want add the parse info to {path}?")
    msgbox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msgbox.setDefaultButton(QtWidgets.QMessageBox.No)
    ret = msgbox.exec()
    if ret == QtWidgets.QMessageBox.No or ret == 0:
        return
    txt = open(path, "r").read()
    newparseinfo["comment"] = "#"  # we need to do this, bc we use # as comment key
    origmetadata["parseinfo"] = newparseinfo
    metastr = "#" + json.dumps(origmetadata, indent=4).replace("\n", "\n#") + "\n"
    txt = metastr + txt
    open(path, "w").write(txt)


def getParseInfo(path):
    with open(path, "r") as f:
        md = getMetadata(f)
    dct = md.get("parseinfo", {})
    if dct:
        peekdf = peekCSV(path, dct)
        invalid = peekdf.empty or len(peekdf.columns) < 2
        if not invalid:
            return dct, True
    dlg = ParserDialog(path)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    ret = dlg.exec()
    dct = dlg.result
    return dct, ret != 0


def peekCSV(path, cfg):
    N = 100
    firstlines = []
    try:
        with open(path, "r") as f:
            for _ in range(N):
                sline = f.readline().strip()
                firstlines.append(sline)
        head = io.StringIO("\n".join([x for x in firstlines if x]))
        df = readCSV(head, cfg)
    except Exception:
        df = DataFrame()
    return df


def getMetadata(f):
    dct = {}
    rawlines = []
    while True:
        line = f.readline()
        if not line.startswith("#"):
            break
        rawlines.append(line[1:])
    if rawlines:
        try:
            dct = json.loads("".join(rawlines))
        except json.decoder.JSONDecodeError:
            dct = {}
    metadataCleanup(dct)
    f.seek(0)
    return dct


def metadataCleanup(dct):
    for k, v in dct.items():
        if isinstance(v, dict):
            metadataCleanup(v)
            continue


class ParserDialog(QtWidgets.QDialog):
    readySig = QtCore.Signal()

    def __init__(self, path):
        N = 100
        pg.mkQApp()
        super().__init__()
        self.setWindowTitle(f"parser cfg for {path}")

        self.result = {}

        la = QtWidgets.QVBoxLayout()
        la.setContentsMargins(0, 0, 0, 0)
        la.setSpacing(0)
        contents = QtWidgets.QHBoxLayout()
        contents.setContentsMargins(0, 0, 0, 0)
        contents.setSpacing(0)

        cfgl = QtWidgets.QVBoxLayout()
        cfgLayout = QtWidgets.QGridLayout()
        cfgLayout.setSpacing(0)
        cfgLayout.setContentsMargins(0, 0, 0, 0)
        cfgscroll = QtWidgets.QScrollArea()
        cfgcontainer = QtWidgets.QWidget()
        cfgcontainer.setMaximumWidth(400)
        cfgcontainer.setLayout(cfgLayout)
        link = "https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html"
        lbl = QtWidgets.QLabel(f'parser cfg <a href="{link}">(?)</a>')
        lbl.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        lbl.setOpenExternalLinks(True)
        cfgl.addWidget(lbl)

        fulldoc = inspect.getdoc(read_csv)
        params = inspect.signature(read_csv)
        paramsFromFulldoc = self.extractParamDesc(fulldoc, params)
        paramsFromFulldoc.pop("filepath_or_buffer")
        self.cfgItems = []
        for idx, (k, v) in enumerate(paramsFromFulldoc.items()):
            lbl = QtWidgets.QLabel(k)
            lbl.setFixedWidth(180)
            val = QtWidgets.QLineEdit()
            val.setPlaceholderText(v)
            val.setToolTip(v)
            val.setFixedWidth(200)
            val.editingFinished.connect(self.parse)
            cfgLayout.addWidget(lbl, idx, 0)
            cfgLayout.addWidget(val, idx, 1)
            self.cfgItems.append((k, val))
        self.cfgItems = dict(self.cfgItems)

        cfgscroll.setWidget(cfgcontainer)
        cfgl.addWidget(cfgscroll)

        dl = QtWidgets.QVBoxLayout()
        self.display = QtWidgets.QPlainTextEdit()
        self.display.setReadOnly(True)
        self.display.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        dl.addWidget(QtWidgets.QLabel(f"parser result preview (first {N} lines)"))
        dl.addWidget(self.display)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()
        self.apply = QtWidgets.QPushButton("apply")
        buttons.addWidget(self.apply)
        self.apply.clicked.connect(self.applyfun)

        contents.addLayout(cfgl)
        contents.addLayout(dl)
        la.addLayout(contents)
        la.addLayout(buttons)
        self.setLayout(la)

        self.resize(800, 600)

        firstlines = []

        with open(path, "r") as f:
            for _ in range(N):
                sline = f.readline().strip()
                firstlines.append(sline)
        self.head = io.StringIO("\n".join([x for x in firstlines if x]))
        metadata = getMetadata(self.head)
        self.parse(metadata.get("parseinfo", {}))
        QtCore.QTimer.singleShot(0, self.readySig.emit)

    def applyfun(self):
        self.accept()

    def parsecfg(self, existingCfg={}):
        dctentries = []
        for k, v in existingCfg.items():
            if k in self.cfgItems:
                if isinstance(v, str):
                    v = '"' + v + '"'
                dctentries.append(f'"{k}":{v}')
        for k, v in self.cfgItems.items():
            v = v.text()
            if not v:
                continue
            dctentries.append(f'"{k}":{v}')

        if not dctentries:
            return {}, True
        dcttext = "{" + ",".join(dctentries) + "}"
        dct = json.loads(dcttext)
        for k, v in dct.items():
            self.cfgItems[k].setText(v)
        return dct, True

    def parse(self, cfg=None):
        if cfg is None:
            cfg = {}
        cfg, cfgvalid = self.parsecfg(cfg)
        if cfgvalid:
            self.head.seek(0)
            df = readCSV(self.head, cfg)
        if not cfgvalid or df.empty:
            txt = [
                "The given cfg did not produce a valid dataframe.\n",
                "The raw file contents are:\n",
                "---\n",
                "\n",
            ]
            self.head.seek(0)
            txt.extend(self.head.readlines())
            self.head.seek(0)
            self.display.setReadOnly(False)
            self.display.setPlainText("".join(txt))
            self.display.setReadOnly(True)
            self.apply.setEnabled(False)
            self.result = {}
        else:
            self.display.setPlainText(
                "Columns:\n---\n" + repr(df.columns) + "\n\nData\n---\n" + repr(df)
            )
            self.apply.setEnabled(True)
            self.result = cfg

    def extractParamDesc(self, txt, params):
        lines = txt.split("\n")
        paragraphs = []
        pdict = {}
        inparagraph = False
        pstart = 0
        pend = 0
        for idx, line in enumerate(lines[:-1]):
            if inparagraph and not line.startswith(" ") and bool(line):
                pend = idx
                paragraphs.append((pstart, pend))
                inparagraph = False
            if (
                not inparagraph
                and not line.startswith(" ")
                and lines[idx + 1].startswith(" ")
                and lines[idx + 1]
            ):
                inparagraph = True
                pstart = idx
        for p in paragraphs:
            ptext = lines[p[0] : p[1]]
            p0split = ptext[0].split(":")
            p0split[-1] += "."
            if len(p0split) < 2:
                p0split.append("")
            pname = p0split[0].strip()
            pdesc = p0split[1].strip() + " " + " ".join(x.strip() for x in ptext[1:])
            pdict[pname] = pdesc
        return pdict
