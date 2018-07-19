import pandas as pd
import numpy as np
from tradeframework.api import Model

import quantutils.model.utils as mlutils
import quantutils.dataset.pipeline as ppl
from quantutils.api.marketinsights import MarketInsights
from quantutils.api.functions import Functions
from quantutils.api.assembly import MIAssembly

class MarketInsightsV2Model(Model):
	def __init__(self, name, env, mi_creds, fun_creds, dataset_id, training_run_id, threshold):
		Model.__init__(self, name, env)
		
		self.miassembly = MIAssembly(MarketInsights(mi_creds), Functions(fun_creds))
		self.dataset_id = dataset_id
		self.training_run_id = training_run_id
		self.threshold = threshold

		return
	
	# Generate Signals and use them with asset values to calculate allocations	
	# TODO : Handle list of assetInfos
	def handleData(self, context, assetInfo):
		Model.handleData(self, context, assetInfo)

		assetValues = assetInfo.values
		
		# Obtain the signals for the next n steps from the Market Insights API
		signals = pd.DataFrame(np.zeros((len(assetValues), 2)), index=assetValues.index, columns=["bar","gap"])
		predictions = self.getPredictions(assetValues.index[0].isoformat(), assetValues.index[-1].isoformat())

		signals.update(predictions)
			
		return self.getDerivativeInfo(context, [assetInfo], [signals])

	def getPredictions(self, start, end):
		predictions = self.miassembly.get_predictions_with_dataset_id(self.dataset_id, self.training_run_id, start=start, end=end) 
		signals = mlutils.getPredictionSignals(ppl.onehot(predictions.values), self.threshold)

		return pd.DataFrame(np.array([signals, np.zeros(len(signals))]).T, index=predictions.index, columns=["bar","gap"])



