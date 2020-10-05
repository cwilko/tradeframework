import pandas as pd
import numpy as np
from tradeframework.api import Model, append_asset

import quantutils.dataset.pipeline as ppl


class MeanReversion(Model):

    def __init__(self, name, env, start=None, end=None):
        Model.__init__(self, name, env)
        self.start = start
        self.end = end
        self.env
        return

    @append_asset
    def handleData(self, asset):
        Model.handleData(self, asset)

        signals = pd.DataFrame(np.zeros((len(asset.values), 2)), index=asset.values.index, columns=["bar", "gap"])

        if (self.start is not None):
            scope = ppl.cropTime(asset.values, self.start, self.end)
        else:
            scope = asset.values

        sig = signals.loc[scope.index]
        sig["bar"] = np.negative(np.sign((asset.values["Close"] - asset.values["Open"]).shift(1).loc[scope.index]))
        signals.loc[sig.index] = sig

        return self.update([asset], [signals])
