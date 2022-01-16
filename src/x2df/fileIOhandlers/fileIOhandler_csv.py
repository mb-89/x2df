from x2df.fileIOhandlers.__fileIOhandler__ import FileIOhandler
import copy
from pandas import DataFrame, read_csv
import json
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import io
import inspect

# we want to do the imports as late as possible to
# keep it snappy once we have more and more fileIOhandlers


class Handler(FileIOhandler):
    def dump(self, df, dst):
        csvstring = '#{"parseinfo":{"comment":"#"}}\n' + df.to_csv(index=False)
        open(dst, "w").write(csvstring)

    def parse(self, path, postprocess=True):
        import pandas as pd

        # since csvs are not a well-defined format, lets try a few things:
        # first, check if the file starts with a metadata comment,
        #  we take the parser args from there
        with open(path, "r") as f:
            origmetadata = getMetadata(f)
        metadata = copy.deepcopy(origmetadata)
        skip = False
        dfraw = DataFrame()
        while not skip:
            # if we dont have parser args, we ask for them with a gui
            if not metadata.get("parseinfo"):
                metadata["parseinfo"], skip = self.getParseInfoViaGUI(path)
            try:
                dfraw = pd.read_csv(path, **metadata["parseinfo"])
            except Exception:
                metadata["parseinfo"] = {}
                continue
            break  # if we are here, we succeeded and dfraw contains a valid dataframe

        # if the parsing was successfull and we changed the original metadata,
        # ask if we should add the metadata to the top of the file.
        if origmetadata != metadata:
            self.updateOrigMetadata(path, metadata)

        if postprocess:
            return self.processRawDF(dfraw)
        else:
            return [dfraw]

    def claim(self, path):
        if path.endswith(".csv"):
            return [path]
        else:
            return []

    def getParseInfoViaGUI(self, path):
        dct = {}
        dlg = ParserDialog(path)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()
        ret = dlg.exec()
        skip = ret == 0
        dct = dlg.result
        return dct, skip

    def updateOrigMetadata(self, path, dct):
        return


def getMetadata(f):
    dct = {}
    rawlines = []
    while True:
        line = f.readline()
        if not line.startswith("#"):
            break
        rawlines.append(line[1:])
    if rawlines:
        dct = json.loads("".join(rawlines))
    return dct


class ParserDialog(QtWidgets.QDialog):
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
                while not sline:
                    sline = f.readline().strip()
                firstlines.append(sline)
        self.head = io.StringIO("\n".join([x for x in firstlines if x]))
        metadata = getMetadata(self.head)
        self.head.seek(0)
        self.parse(metadata.get("parseinfo", {}))

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
        try:
            dct = json.loads(dcttext)
        except Exception:
            return {}, False
        for k, v in dct.items():
            self.cfgItems[k].setText(v)
        return dct, True

    def parse(self, cfg={}):
        cfg, cfgvalid = self.parsecfg(cfg)
        if cfgvalid:
            try:
                self.head.seek(0)
                df = read_csv(self.head, **cfg)
            except Exception:
                df = DataFrame()
                cfgvalid = False
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
