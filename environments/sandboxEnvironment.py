# ======================          
# SpreadsEnvironment Class
#
# For representing a Spread Betting trading platform
# ======================

from api import TradeEnvironment, Context
from engines import BaselineEngine
from txMgr import SpreadsTxMgr, NullTxMgr

class SandboxEnvironment(TradeEnvironment):
	def __init__(self, name):
		TradeEnvironment.__init__(self, name)
		self.engine = BaselineEngine("Sandbox Engine", SpreadsTxMgr())
		self.index = 0

	def handleData(self, context, data):
		TradeEnvironment.handleData(self, context, data)
		# Mediate between our Portfolio and the Environment
		self.index += len(data)
		return self.portfolio.handleData(context, data, self.index)

	def createTradeEngine(self, name):
		return BaselineEngine(name, NullTxMgr())

	def placeOrders(self, context, allocations, data):
		ret = self.engine.executeTrades(data, allocations)
		context['portfolio_returns'] = ret

class SandboxContext(Context):
	def __init__(self, context):
		self.context = context
		return