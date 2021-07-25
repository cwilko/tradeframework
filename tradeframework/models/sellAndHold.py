import pandas as pd
import numpy as np
from tradeframework.api import Model
import quantutils.dataset.pipeline as ppl


class SellAndHold(Model):

    def __init__(self, name, env, start=None, end=None):
        Model.__init__(self, name, env)
        self.start = start
        self.end = end
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, idx=0):

        # Extract window from the data
        # TODO : Handle list of assetInfos
        window = self.getWindow(idx)

        if (self.start is not None):
            signals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])
            signals.ix[ppl.cropTime(signals, self.start, self.end).index] = -1
            signals["gap"] = 0
        else:
            signals = pd.DataFrame(np.negative(np.ones((len(window), 2))), index=window.index, columns=["bar", "gap"])

        return signals[idx:]
