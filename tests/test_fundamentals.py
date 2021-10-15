from x2df import x2df
from x2df import logfuns


def test_main():
    assert logfuns.setupLogging() == 0  # first pass for logging setup
    assert logfuns.setupLogging() == -1  # second pass: skipped bc already set up
    assert x2df.main(["test"]) == 0


if __name__ == "__main__":
    test_main()
