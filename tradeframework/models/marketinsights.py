import pandas as pd
import numpy as np
from tradeframework.api import Model

from quantutils.api.marketinsights import MarketInsights

class MarketInsightsModel(Model):
	def __init__(self, name, env, creds, mkt, modelId, threshold):
		Model.__init__(self, name, env)

		self.mi = MarketInsights(creds)
		self.modelId = modelId
		self.mkt = mkt
		self.threshold = threshold

		return
	
	# Generate Signals and use them with asset values to calculate allocations	
	def handleData(self, context, assetInfo):
		Model.handleData(self, context, assetInfo)

		assetValues = assetInfo.values
		
		# Obtain the signals for the next n steps from the Market Insights API
		signals = pd.DataFrame(np.zeros((len(assetValues), 2)), index=assetValues.index, columns=["bar","gap"])
		predictions = self.getPredictions(assetValues.index[0].isoformat(), assetValues.index[-1].isoformat())

		signals.update(predictions)
			
		return self.getDerivativeInfo(context, assetInfo, signals)

	def getPredictions(self, start, end):

		predictions = self.mi.get_predictions(self.mkt, self.modelId, start=start, end=end) 
		signals = np.ones(len(predictions))
		a = np.argmax(predictions.values,axis=1)
		signals[(a==1)] = -1 # Set any DOWN signals to -1 (UP signals will pick up the default of 1)
		signals[(predictions.values < self.threshold).all(axis=1)] = 0

		return pd.DataFrame(np.array([signals, signals]).T, index=predictions.index, columns=["bar","gap"])



