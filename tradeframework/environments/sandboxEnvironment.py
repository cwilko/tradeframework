# ======================
# SpreadsEnvironment Class
#
# For representing a Spread Betting trading platform
# ======================

from tradeframework.api import TradeEnvironment
from tradeframework.engines import BaselineEngine
from tradeframework.tx import SpreadsTxMgr


class SandboxEnvironment(TradeEnvironment):

    def __init__(self, name):
        TradeEnvironment.__init__(self, name)
        self.tradeEngine = BaselineEngine("Sandbox Engine", SpreadsTxMgr())

    def handleData(self, asset):
        TradeEnvironment.handleData(self, asset)
        # Mediate between our Portfolio and the Environment
        return self.portfolio.handleData(asset)
