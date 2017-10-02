from . import Strategy
import pandas as pd

# ======================          
# Portfolio Class
# ======================

class Portfolio(Strategy):

	def __init__(self, name, env):
		Strategy.__init__(self, name, env)
		self.strategy_list = []

	def createPortfolio(self, name):
		portfolio = Portfolio(name, self.env)
		self.strategy_list.append(portfolio)
		return portfolio

	def addModel(self, model):
		self.strategy_list.append(model)
		return model

	def handleData(self, context, data, index):

		# Update all children
		signals = [strategy.handleData(context, data, index) for strategy in self.strategy_list]

		# Calculate optimal portfolio allocation
		n = len(self.strategy_list)
		F = [(1.0/n)] * n
		signals = [a*b for a,b in zip(signals,F)]

		# Calculate portfolio returns
		#self.returns = sRet.dot(np.transpose(F2))

		# Return portfolio allocations
		return pd.concat(signals, join="outer", axis=1, keys=[s.getName() for s in self.strategy_list])