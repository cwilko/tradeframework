# ======================          
# TradeEnvironment Class
# ======================

from . import Portfolio
import models as md

class TradeEnvironment():

	def __init__(self, name):
		self.name = name
		self.portfolio = Portfolio(name + "_Portfolio", self)
		return

	def createPortfolio(self, name):
		return self.portfolio.createPortfolio(name)

	def createTradeEngine(self):
		pass

	def createModel(self, modelClass, modelName):
		modelInstance = getattr(md, modelClass)
		model = modelInstance(modelName, self)
		return model

	def handleData(self, context, data):
		pass
		

class Context:
	def __init__(self):
		pass