from pipreqs import pipreqs
import os
import os.path as op


def main():
    wd = op.dirname(__file__)
    dst = op.join(wd, "requirements.txt")

    try:
        os.remove(dst)
    except FileNotFoundError:
        pass
    pipreqs.main()
    unsorted = open(dst, "r").readlines()
    sortedlst = sorted(unsorted)
    open(dst, "w").write("".join(sortedlst))


if __name__ == "__main__":
    main()
