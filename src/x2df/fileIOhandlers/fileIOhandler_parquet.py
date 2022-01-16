from x2df.fileIOhandlers.__fileIOhandler__ import FileIOhandler

# we want to do the imports as late as possible to
# keep it snappy once we have more and more fileIOhandlers


class Handler(FileIOhandler):
    def dump(self, df, dst, **kwargs):
        # we import pyarrow here to make sure that is found by pyreqs.
        # if it is not found, we get an error and need to install it.
        if not dst:
            return
        import pyarrow  # noqa: F401

        df.to_parquet(dst)

    def parse(self, path, postprocess=True):
        import pyarrow  # noqa: F401
        import pandas as pd

        dfraw = pd.read_parquet(path)
        if postprocess:
            return self.processRawDF(dfraw)
        else:
            return [dfraw]

    def claim(self, path):
        import pyarrow  # noqa: F401

        try:
            pyarrow.parquet.read_schema(path)
            return [path]
        except:  # noqa: E722 #this is fine. Reject any exception but never crash.
            return []
