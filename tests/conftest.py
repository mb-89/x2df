import pytest
from x2df import examples


@pytest.fixture(scope="session")
def exampleDataFilePaths(request, tmpdir_factory):
    ex = request.param
    dst = tmpdir_factory.mktemp("exampledata")
    src = examples.createExampleFile(ex, dst)
    return src
