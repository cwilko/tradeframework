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

    def append(self, asset):
        TradeEnvironment.append(self, asset)
        # Mediate between our Portfolio and the Environment
        return self.portfolio.append(asset)
