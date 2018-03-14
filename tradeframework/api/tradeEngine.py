# ======================          
# TradeEngine Class
# ======================
class TradeEngine:

	BUY = 1
	CASH = 0
	SELL = -1
	
	def __init__(self, name, txMgr):
		self.name = name
		self.txMgr = txMgr
	
	def executeTrades(self, data, signals):
		pass

	# f(Pin, A) => R
	def getReturns(self, assetValues, allocations):
		pass

	# f(Pin,A) => Pout
	def getDerivativeInfo(self, assetInfo, weights):
		pass


	# f(Pin,A) => Pout
	def getDerivativeValues(self, assetValues, allocations):
		pass

	# Helper method to merge bar and gap returns into a single period
	@staticmethod
	def getPeriodReturns(returns):
		returns = (returns + 1).prod(axis=1)-1
		returns.columns = ["period"]
		return returns

class AssetInfo:
	def __init__(self, name, values):
		self.name = name
		self.values = values
		
class DerivativeInfo(AssetInfo):
	def __init__(self, name, values, allocations, weights, returns):
		AssetInfo.__init__(self, name, values)
		self.allocations = allocations		
		self.weights = weights
		self.returns = returns