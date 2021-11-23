from x2df.examples.__example__ import AbstractExample
from math import pi
from numpy import linspace
from pandas import DataFrame
import numpy as np
from scipy import integrate
from math import sin
from functools import cache


class Example(AbstractExample):
    @cache
    def createDF(self):

        ts = 0.0005

        rampup = linspace(0, 2000, int(30 / ts))
        hold1 = linspace(2000, 2000, int(5 / ts))
        rd2 = np.fromiter(
            (2000 - 1000 * pow(x, 0.5) for x in np.arange(0, 1, 1 / int(10 / ts))),
            float,
        )
        hold2 = linspace(1000, 1000, int(5 / ts))
        rd3 = linspace(1000, 0, int(2.5 / ts))
        signalWOharmonics = np.concatenate([rampup, hold1, rd2, hold2, rd3])
        t = np.fromiter(range(0, len(signalWOharmonics)), int) * ts

        rpm2rads = 1 / 60 * 2 * pi
        angle = integrate.cumtrapz(signalWOharmonics * rpm2rads, t, initial=0)

        # add a first harmonic
        A1 = 5 * np.fromiter((min(x / 250, 1) for x in signalWOharmonics), float)
        H1 = A1 * np.fromiter((sin(x) for x in angle), float)

        # add a third harmonic
        A3 = 3 * np.fromiter((min(x / 250, 1) for x in signalWOharmonics), float)
        H3 = A3 * np.fromiter((sin(x * 3) for x in angle), float)

        signalWithHarmonics = signalWOharmonics + H1 + H3

        df = DataFrame()
        df["time/s"] = t
        df["angspd/rpm"] = signalWithHarmonics
        df["angspd2/rpm"] = signalWithHarmonics * 1.25
        df.set_index("time/s")
        return df
