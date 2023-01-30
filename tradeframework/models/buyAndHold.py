import pandas as pd
import numpy as np
from tradeframework.api import Model
import quantutils.dataset.pipeline as ppl


class BuyAndHold(Model):

    def __init__(self, name, env, start=None, end=None, barOnly=False):
        Model.__init__(self, name, env)
        self.start = start
        self.end = end
        self.barOnly = barOnly
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, idx=0):

        # Extract window from the data
        # TODO : Handle list of assetInfos
        # TODO : Handle ohlc from portfolio as an asset
        # TODO : Handle missing data (nans)
        window = self.getWindow(idx)

        if (self.start is not None):
            signals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])
            signals.loc[ppl.cropTime(signals, self.start, self.end).index] = 1
        else:
            signals = pd.DataFrame(np.ones((len(window), 2)), index=window.index, columns=["bar", "gap"])

        if (self.barOnly):
            signals["gap"] = 0

        return signals[idx:]
