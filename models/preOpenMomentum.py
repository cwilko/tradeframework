import pandas as pd
import numpy as np
import strategies as st
from .. import Model

class PreOpenMomentum(Model):
	def __init__(self, name, env):
		Model.__init__(self, name, env)
		return
		
	def handleData(self, context, data, index):
		Model.handleData(self, context, data, index)
		
		# Create context space
		if self.name not in context:
			context[self.name] = {'prevClose': pd.DataFrame()}

		# Generate new signals
		context[self.name]['prevClose'] = pd.concat([context[self.name]['prevClose'], data[(data.index.hour == 21) & (data.index.minute == 00)].resample('B').agg({'Open': 'first'}).fillna(method='ffill').shift(1).dropna()])
		context[self.name]['currentSignal'] = Model.CASH
		# Need to generate the signals for the next n steps
		newSignals = data.groupby(data.index).apply(lambda x: gap_close_predict(x, context[self.name]))
		#print newSignals["2016-09-01 11:50:00":]
		self.signals = pd.concat([self.signals, newSignals], join="outer", axis=0)

		# Update base returns for optimisation purposes 
		self.tEngine.executeTrades(data, self.signals)

		return self.signals

# Whichever direction the market has moved by morning EST, trade in the same direction until the close.
def gap_close_predict(ohlc, context):
	allocation = pd.Series({'bar':Model.CASH, 'gap':Model.CASH})

	if ohlc.index.date in context['prevClose'].index.date:

		if (ohlc.index.hour == 12) & (ohlc.index.minute == 0):
			if (ohlc.Open[0] > context['prevClose'].loc[ohlc.index.date].Open[0]):
				context['currentSignal'] = Model.BUY
			else:
				context['currentSignal'] = Model.SELL

		if (ohlc.index.hour >= 12) & (ohlc.index.hour <= 20):
			allocation = pd.Series({'bar':context['currentSignal'], 'gap':context['currentSignal']})
			
	return allocation
	

