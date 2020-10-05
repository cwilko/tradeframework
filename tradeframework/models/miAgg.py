import pandas as pd
import numpy as np
from tradeframework.api import Model, append_asset

import quantutils.model.utils as mlutils
import quantutils.dataset.pipeline as ppl
from quantutils.api.marketinsights import MarketInsights
from quantutils.api.functions import Functions
from quantutils.api.assembly import MIAssembly


class MIAggregateModel(Model):

    def __init__(self, name, env, credstore, mi_models, aggMethod, threshold):
        Model.__init__(self, name, env)

        self.miassembly = MIAssembly(MarketInsights(credstore), Functions(credstore))
        self.modelConfig = mi_models
        self.aggMethod = aggMethod
        self.threshold = threshold

        return

    # Generate Signals and use them with asset values to calculate allocations
    # TODO : Handle list of assetInfos
    @append_asset
    def handleData(self, asset):
        Model.handleData(self, asset)

        assetValues = asset.values
        signals = pd.DataFrame(np.zeros((len(assetValues), 2)), index=assetValues.index, columns=["bar", "gap"])

        # Obtain the signals for the next n steps from the Market Insights api
        predictions = self.getPredictions(assetValues.index[0].isoformat(), assetValues.index[-1].isoformat())

        signals.update(predictions)

        return self.update([asset], [signals])

    def getPredictions(self, start, end):

        predictions_list = []

        for training_run in self.modelConfig:
            for dataset_id in training_run["datasets"]:
                print("Retrieving predictions for training id {}, dataset {}".format(training_run["training_run_id"], dataset_id))
                predictions_list.append(self.miassembly.get_predictions_with_dataset_id(dataset_id, training_run["training_run_id"], start=start, end=end))

        predictions = mlutils.aggregatePredictions(predictions_list, self.aggMethod)
        signals = mlutils.getPredictionSignals(ppl.onehot(predictions.values), self.threshold)

        return pd.DataFrame(np.array([signals, np.zeros(len(signals))]).T, index=predictions.index, columns=["bar", "gap"])
