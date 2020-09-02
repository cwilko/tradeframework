# ======================
# SpreadsEnvironment Class
#
# For representing a Spread Betting trading platform
# ======================

from tradeframework.api import TradeEnvironment, Context
from tradeframework.engines import BaselineEngine
from tradeframework.tx import SpreadsTxMgr, NullTxMgr


class SandboxEnvironment(TradeEnvironment):

    def __init__(self, name):
        TradeEnvironment.__init__(self, name)
        self.tradeEngine = BaselineEngine("Sandbox Engine", SpreadsTxMgr())

    def handleData(self, context, assetInfo):
        TradeEnvironment.handleData(self, context, assetInfo)
        # Mediate between our Portfolio and the Environment
        return self.portfolio.handleData(context, assetInfo)

    def createTradeEngine(self, name):
        return BaselineEngine(name, NullTxMgr())

    def placeOrders(self, context, allocations, assetInfo):
        return self.tradeEngine.getReturns(assetInfo, allocations)

    def getTradingInfo(self, context, dInfo, startCapital=1):
        return self.tradeEngine.getTradingInfo(dInfo, startCapital)


class SandboxContext(Context):

    def __init__(self, context):
        self.context = context
        return
