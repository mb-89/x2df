from x2df.examples.__example__ import AbstractExample
from scipy import signal
from math import pi
from numpy import linspace
from pandas import DataFrame


class Example(AbstractExample):
    def createDF(self):
        f = 10
        omega = 2 * pi * f
        Ds = linspace(0.1, 2, 10)
        df = DataFrame()
        t = linspace(0, 10 * 1 / f, 500)
        df["time/s"] = t
        for D in Ds:
            lti = signal.lti([omega ** 2], [1.0, 2 * D * omega, omega ** 2])
            t, y = signal.step(lti, T=t)
            df[f"D={D:.2f}"] = y
        df.set_index("time/s")
        return df
