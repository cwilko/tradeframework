import pandas as pd
from tradeframework.api import Model

class PreOpenMomentum(Model):
	def __init__(self, name, env):
		Model.__init__(self, name, env)
		return

	# TODO : Handle list of assetInfos
	def handleData(self, context, assetInfo):
		Model.handleData(self, context, assetInfo)
		
		# Generate Signals and use them with asset values to calculate allocations

		# Create context space
		if self.name not in context:
			context[self.name] = {}
			context[self.name]['temp'] = {'data': pd.DataFrame(), 'currentSignal': Model.CASH }

		assetValues = assetInfo.values

		# Extract the relevant asset information
		context[self.name]['temp']['data'] = pd.concat([context[self.name]['temp']['data'], assetValues[(assetValues.index.hour == 16) & (assetValues.index.minute == 00)].resample('B').agg({'Open': 'first'}).fillna(method='ffill').shift(1).dropna()])
		# Generate the signals for the next n steps
		signals = assetValues.groupby(assetValues.index).apply(lambda x: gap_close_predict(x, context[self.name]['temp']))
		#self.signals = pd.concat([self.signals, newSignals], join="outer", axis=0)
		
		del context[self.name]['temp']
		
		return self.getDerivativeInfo(context, [assetInfo], [signals])

# Whichever direction the market has moved by morning EST, trade in the same direction until the close.
def gap_close_predict(ohlc, context):
	signal = pd.Series({'bar':Model.CASH, 'gap':Model.CASH})

	if ohlc.index.date in context['data'].index.date:

		if (ohlc.index.hour == 7) & (ohlc.index.minute == 0):
			if (ohlc.Open[0] > context['data'].loc[ohlc.index.date].Open[0]):
				context['currentSignal'] = Model.BUY
			else:
				context['currentSignal'] = Model.SELL

		if (ohlc.index.hour >= 7) & (ohlc.index.hour <= 15):
			signal = pd.Series({'bar':context['currentSignal'], 'gap':context['currentSignal']})
			
	return signal
	

