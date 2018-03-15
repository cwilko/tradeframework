# ======================          
# TradeEnvironment Class
# ======================

from . import Portfolio
import tradeframework.optimizers as opt
import tradeframework.models as md


class TradeEnvironment():

	def __init__(self, name):
		self.name = name
		self.portfolio = Portfolio(name + "_Portfolio", self)
		return

	def createPortfolio(self, name, optimizer=None):
		return self.portfolio.createPortfolio(name, optimizer)

	def createTradeEngine(self):
		pass

	def createModel(self, modelClass, modelName, args=()):
		modelInstance = getattr(md, modelClass)
		model = modelInstance(modelName, self, *args)
		return model

	def createOptimizer(self, optClass, optName, opts={}):
		optInstance = getattr(opt, optClass)
		optimizer = optInstance(optName, self, **opts)
		return optimizer

	def handleData(self, context, assetInfo):
		pass
		

class Context:
	def __init__(self):
		pass