try:  # pragma: no cover
    from x2df.x2df import main  # pragma: no cover
    from x2df.logfuns import setupLogging  # pragma: no cover
except ModuleNotFoundError:  # pragma: no cover
    # we need this so the vscode debugger works better
    from x2df import main  # pragma: no cover
    from logfuns import setupLogging  # pragma: no cover

import sys  # pragma: no cover

setupLogging()  # pragma: no cover
main(sys.argv)  # pragma: no cover
