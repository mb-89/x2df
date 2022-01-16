class FileIOhandler:
    def dump(self, df, dst=None, **kwargs):
        """dumps the given dataframe to the given file."""
        raise NotImplementedError

    def parse(self, path, postprocess=True):
        """parses the given path and returns a list of extracted dataframes."""
        raise NotImplementedError

    def claim(self, path):
        """checks if this handler can parse the given path.
        Returns a list of paths that are claimed for parsing the given path"""
        raise NotImplementedError

    def processRawDF(self, df):
        """does general postprocessing on raw dataframes that needs to be identical
        for all types of datafiles."""
        self._findIndex(df)
        return [df]

    def _findIndex(self, df):

        # check if we have one unique time col
        timecols = [x for x in df.columns if "time" in x]
        if len(timecols) == 1:
            df.set_index(timecols[0], inplace=True)
            return
