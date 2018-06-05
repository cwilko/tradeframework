import pandas as pd
import numpy as np
from tradeframework.api import Model

class SellAndHold(Model):
	def __init__(self, name, env):
		Model.__init__(self, name, env)
		return
	
	# TODO : Handle list of assetInfos
	def handleData(self, context, assetInfo):
		Model.handleData(self, context, assetInfo)
		
		# Generate Signals and use them with asset values to calculate allocations

		# Generate the signals for the next n steps
		#signals = data.groupby(data.index).apply(lambda x: gap_close_predict(x, context[self.name]['temp']))
		#self.signals = pd.concat([self.signals, newSignals], join="outer", axis=0)
		signals = pd.DataFrame(0 - np.ones((len(assetInfo.values), 2)), index=assetInfo.values.index, columns=["bar","gap"])

		return self.getDerivativeInfo(context, [assetInfo], [signals])