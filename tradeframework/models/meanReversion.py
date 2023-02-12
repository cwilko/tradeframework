import pandas as pd
import numpy as np
from tradeframework.api import Model

import quantutils.dataset.pipeline as ppl


class MeanReversion(Model):

    def __init__(self, env, start=None, end=None, barOnly=False):
        Model.__init__(self, env)
        self.start = start
        self.end = end
        self.window = 1
        self.barOnly = barOnly
        return

    # Generate Signals and use them with asset values to calculate allocations
    # NOTE: This implement mean reversion per period. E.g if you provide 5-min date, it will mean revert every 5 mins.
    def getSignals(self, window, idx=0):

        s = np.insert(np.negative(np.sign(np.diff(window["Open"]))), 0, 0)
        signals = pd.DataFrame(np.array([s, s]).T, index=window.index, columns=["bar", "gap"])

        if (self.start is not None):
            scope = ppl.cropTime(signals, self.start, self.end)
            scopedSignals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])
            scopedSignals.loc[scope.index] = scope.values
            signals = scopedSignals

        if (self.barOnly):
            signals["gap"] = 0

        return signals[idx:]
