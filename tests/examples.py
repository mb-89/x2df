from abc import ABC, abstractmethod
import inspect
import sys


class ExampleDataFileCreator(ABC):
    @abstractmethod
    def createFile(self, dst):
        """creates a file containing example data, puts it in the provided dst folder
        and returns the path to the created file."""


# put example file creators here: ----------------------------------------
class Stepresponses1(ExampleDataFileCreator):
    def createFile(self, dst):
        fn = dst / "Stepresponses1.parquet"
        open(fn, "w").write("test")
        return fn


class Sweep1(ExampleDataFileCreator):
    def createFile(self, dst):
        fn = dst / "Sweep1.parquet"
        open(fn, "w").write("test")
        return fn


# these functions will be used by the rest of the code to fetch examples -
def is_ExampleDataFileCreator_subclass(o):
    return (
        inspect.isclass(o)
        and issubclass(o, ExampleDataFileCreator)
        and not o == ExampleDataFileCreator
    )


def getExampleNameList():
    lst = (
        x
        for x in inspect.getmembers(
            sys.modules[__name__], predicate=is_ExampleDataFileCreator_subclass
        )
    )
    return [x[0] for x in lst]


def createExampleFile(name, dst):
    dct = dict(
        (
            x
            for x in inspect.getmembers(
                sys.modules[__name__], predicate=is_ExampleDataFileCreator_subclass
            )
        )
    )
    C = dct.get(name)
    if C is None:
        return None
    return C().createFile(dst)
