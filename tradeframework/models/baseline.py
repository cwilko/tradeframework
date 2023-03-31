import pandas as pd
import numpy as np
from tradeframework.api.core import Model
import quantutils.dataset.pipeline as ppl


class RandomSignals(Model):

    def __init__(self, env, start=None, end=None, barOnly=False):
        Model.__init__(self, env)
        self.start = start
        self.end = end
        self.barOnly = barOnly
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, window, idx=0):

        if (self.start is not None):
            signals = pd.DataFrame(np.round(np.random.rand(len(window), 2)), index=window.index, columns=["bar", "gap"])
            signals[signals == 0] = -1.
            signals.loc[~signals.index.isin(ppl.cropTime(signals, self.start, self.end).index)] = 0
        else:
            signals = pd.DataFrame(np.round(np.random.rand(len(window), 2)), index=window.index, columns=["bar", "gap"])
            signals[signals == 0] = -1

        if (self.barOnly):
            signals["gap"] = 0

        return signals[idx:]


class MaxReturn(Model):

    def __init__(self, env, start=None, end=None, barOnly=False):
        Model.__init__(self, env)
        self.start = start
        self.end = end
        self.barOnly = barOnly
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, window, idx=0):

        signals = pd.DataFrame(np.array([np.sign(window["Close"] - window["Open"]), np.sign(window.shift(-1)["Open"] - window["Close"])]).T, index=window.index, columns=["bar", "gap"])

        if (self.start is not None):
            signals.loc[~signals.index.isin(ppl.cropTime(signals, self.start, self.end).index)] = 0

        if (self.barOnly):
            signals["gap"] = 0

        return signals[idx:]


class MinReturn(Model):

    def __init__(self, env, start=None, end=None, barOnly=False):
        Model.__init__(self, env)
        self.start = start
        self.end = end
        self.barOnly = barOnly
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, window, idx=0):

        signals = pd.DataFrame(np.array([np.sign(window["Open"] - window["Close"]), np.sign(window["Close"] - window.shift(-1)["Open"])]).T, index=window.index, columns=["bar", "gap"])

        if (self.start is not None):
            signals.loc[~signals.index.isin(ppl.cropTime(signals, self.start, self.end).index)] = 0

        if (self.barOnly):
            signals["gap"] = 0

        return signals[idx:]
