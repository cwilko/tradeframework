from . import Derivative

# ======================          
# Model Class
# ======================

class Model(Derivative):

	BUY = 1
	CASH = 0
	SELL = -1

	def __init__(self, name, env):
		Derivative.__init__(self, name, env)
		
	def handleData(self, context, assetInfo):		
		return Derivative.handleData(self, context, assetInfo)

	def getDerivativeInfo(self, context, assetInfo, signals):
		## Get allocations from TradeEngine
		derivInfo = self.env.tradeEngine.getDerivativeInfo(self.name, assetInfo.values, signals)
		
		# Update context 
		if self.name not in context:
			context[self.name] = {}
		context[self.name]['debug'] = derivInfo

		return derivInfo
