import pandas as pd
import numpy as np
from tradeframework.api import Model

import quantutils.model.utils as mlutils
import quantutils.dataset.pipeline as ppl
from quantutils.api.marketinsights import MarketInsights
from quantutils.api.functions import Functions
from quantutils.api.assembly import MIAssembly


class MIBasicModel(Model):

    def __init__(self, name, env, credstore, dataset_id, training_run_id, threshold):
        Model.__init__(self, name, env)

        self.miassembly = MIAssembly(MarketInsights(credstore), Functions(credstore))
        self.dataset_id = dataset_id
        self.training_run_id = training_run_id
        self.threshold = threshold

        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, idx=0):

        # Extract window from the data
        # TODO : Handle list of assetInfos
        window = self.getWindow(idx)

        # Obtain the signals for the next n steps from the Market Insights API
        signals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])
        predictions = self.getPredictions(window.index[0].isoformat(), window.index[-1].isoformat())

        signals.update(predictions)

        return signals[idx:]

    def getPredictions(self, start, end):
        predictions = self.miassembly.get_predictions_with_dataset_id(self.dataset_id, self.training_run_id, start=start, end=end)
        predictions = mlutils.aggregatePredictions([predictions], method="mean_all")
        signals = mlutils.getPredictionSignals(ppl.onehot(predictions.values), self.threshold)

        return pd.DataFrame(np.array([signals, np.zeros(len(signals))]).T, index=predictions.index, columns=["bar", "gap"])
