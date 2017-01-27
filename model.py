from . import Strategy
import pandas as pd

# ======================          
# Model Class
# ======================

class Model(Strategy):

	BUY = 1
	CASH = 0
	SELL = -1

	def __init__(self, name, env):
		Strategy.__init__(self, name, env)
		self.signals = pd.DataFrame(columns=["bar", "gap"])
		
	def handleData(self, context, data, index):		
		return Strategy.handleData(self, context, data, index)
