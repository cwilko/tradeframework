import pandas as pd
import numpy as np
import datetime
from tradeframework.api import Model

import quantutils.model.utils as mlutils
from quantutils.api.marketinsights import MarketInsights
from quantutils.api.functions import Functions
from quantutils.api.assembly import MIAssembly


class MIAggregateModel(Model):

    def __init__(self, name, env, credstore, mi_models, aggMethod, threshold=0, barOnly=False, debug=False):
        Model.__init__(self, name, env)

        self.miassembly = MIAssembly(MarketInsights(credstore), Functions(credstore))
        self.modelConfig = mi_models
        self.aggMethod = aggMethod
        self.threshold = threshold
        self.barOnly = barOnly
        self.debug = debug
        return

    # Generate Signals and use them with asset values to calculate allocations
    def getSignals(self, idx=0):

        # Extract window from the data
        # TODO : Handle list of assetInfos
        window = self.getWindow(idx)

        signals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])

        # Obtain the signals for the next n steps from the Market Insights api
        predictions = self.getPredictions(window.index[0].isoformat(), (window.index[-1] + datetime.timedelta(seconds=1)).isoformat())

        if predictions is not None:
            signals.update(predictions)

        return signals[idx:]

    def getPredictions(self, start, end):

        predictions_list = []

        for training_run in self.modelConfig:
            for dataset_id in training_run["datasets"]:
                print("Retrieving predictions for training id {}, dataset {}".format(training_run["training_run_id"], dataset_id))
                predictions = self.miassembly.get_predictions_with_dataset_id(dataset_id, training_run["training_run_id"], start=start, end=end, debug=self.debug)
                if (predictions is None):
                    return None
                predictions_list.append(predictions)

        predictions = mlutils.aggregatePredictions(predictions_list, self.aggMethod)
        signals = mlutils.getPredictionSignals(predictions.values, self.threshold)
        signals = pd.DataFrame(np.array([signals, signals]).T, index=predictions.index, columns=["bar", "gap"])
        if (self.barOnly):
            signals["gap"] = 0
        return signals
