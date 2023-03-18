import pandas as pd
import numpy as np
import datetime
from tradeframework.api.core import Model

import marketinsights.utils.model as mlutils
from marketinsights.remote.ml import MarketInsights
from marketinsights.remote.ibmcloud import CloudFunctions
from marketinsights.remote.assembly import MarketInsightsAssembly


class MIBasicModel(Model):

    def __init__(self, env, credstore, dataset_id, training_run_id, threshold=0, barOnly=False, debug=False):
        Model.__init__(self, env)

        self.miassembly = MarketInsightsAssembly(MarketInsights(credstore), CloudFunctions(credstore))
        self.dataset_id = dataset_id
        self.training_run_id = training_run_id
        self.threshold = threshold
        self.debug = debug
        self.barOnly = barOnly

        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, window, idx=0):

        # Obtain the signals for the next n steps from the Market Insights API
        signals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])
        predictions = self.getPredictions(window.index[0].isoformat(), (window.index[-1] + datetime.timedelta(seconds=1)).isoformat())

        if predictions is not None:
            signals.update(predictions)

        return signals[idx:]

    def getPredictions(self, start, end):
        predictions = self.miassembly.get_predictions_with_dataset_id(self.dataset_id, self.training_run_id, start=start, end=end, debug=self.debug)
        if predictions is None:
            return predictions
        predictions = mlutils.aggregatePredictions([predictions], method="mean_all")
        signals = mlutils.getPredictionSignals(predictions.values, self.threshold)
        signals = pd.DataFrame(np.array([signals, signals]).T, index=predictions.index, columns=["bar", "gap"])
        if (self.barOnly):
            signals["gap"] = 0
        return signals
