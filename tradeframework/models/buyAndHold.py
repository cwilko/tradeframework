import pandas as pd
import numpy as np
from tradeframework.api import Model, append_asset
import quantutils.dataset.pipeline as ppl


class BuyAndHold(Model):

    def __init__(self, name, env, start=None, end=None):
        Model.__init__(self, name, env)
        self.start = start
        self.end = end
        return

    # TODO : Handle list of assetInfos
    @append_asset
    def handleData(self, asset):

        # Generate Signals and use them with asset values to calculate allocations

        # Generate the signals for the next n steps
        #signals = data.groupby(data.index).apply(lambda x: gap_close_predict(x, context[self.name]['temp']))
        #self.signals = pd.concat([self.signals, newSignals], join="outer", axis=0)

        if (self.start is not None):
            signals = pd.DataFrame(np.zeros((len(asset.values), 2)), index=asset.values.index, columns=["bar", "gap"])
            signals.ix[ppl.cropTime(signals, self.start, self.end).index] = 1
            signals["gap"] = 0
        else:
            signals = pd.DataFrame(np.ones((len(asset.values), 2)), index=asset.values.index, columns=["bar", "gap"])

        return self.update([asset], [signals])
