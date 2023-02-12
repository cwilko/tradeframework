import pandas as pd
import numpy as np
from tradeframework.api import Model
import quantutils.dataset.pipeline as ppl


class CombinationModel(Model):

    def __init__(self, env, modelList=[], start=None, end=None, barOnly=False):
        Model.__init__(self, env)
        self.start = start
        self.end = end
        self.barOnly = barOnly
        self.modelList = modelList
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, window, idx=0):

        n = len(self.modelList)
        assetWeights = np.round(np.sum(np.sign([self.env.getPortfolio().findAsset(model).getWeights()[idx:].values for model in self.modelList]), axis=0) / n)
        signals = pd.DataFrame(assetWeights, index=window.index, columns=["bar", "gap"])

        if (self.start is not None):
            scope = ppl.cropTime(signals, self.start, self.end)
            scopedSignals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])
            scopedSignals.loc[scope.index] = scope.values
            signals = scopedSignals

        if (self.barOnly):
            signals["gap"] = 0

        return signals[idx:]
