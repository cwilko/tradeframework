import pandas as pd
import numpy as np
from tradeframework.api import Model

import quantutils.dataset.pipeline as ppl


class RetraceDailyMove(Model):

    def __init__(self, name, env, start=None, end=None):
        Model.__init__(self, name, env)
        self.start = start
        self.end = end
        self.env
        return

    def handleData(self, asset):
        Model.handleData(self, asset)

        signals = pd.DataFrame(np.zeros((len(asset.values), 2)), index=asset.values.index, columns=["bar", "gap"])

        if (self.start is not None):
            scope = ppl.cropTime(asset.values["Open"], self.start, self.end)
        else:
            scope = asset.values["Open"]

        sig = signals.loc[scope.index][1:]
        sig["bar"] = np.negative(np.sign(np.diff(scope)))
        signals.loc[sig.index] = sig

        return self.update([asset], [signals])
