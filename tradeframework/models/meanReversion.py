import pandas as pd
import numpy as np
from tradeframework.api import Model

import quantutils.dataset.pipeline as ppl


class MeanReversion(Model):

    def __init__(self, name, env, start=None, end=None):
        Model.__init__(self, name, env)
        self.start = start
        self.end = end
        self.env
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, idx=0):

        # Extract window from the data
        # TODO : Handle list of assetInfos
        # TODO: ADD WINDOW SUPPORT
        window = self.assets[0].values[idx:]

        signals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])

        if (self.start is not None):
            scope = ppl.cropTime(window, self.start, self.end)
        else:
            scope = window

        sig = signals.loc[scope.index]
        sig["bar"] = np.negative(np.sign((window["Close"] - window["Open"]).shift(1).loc[scope.index]))
        signals.loc[sig.index] = sig

        return signals
