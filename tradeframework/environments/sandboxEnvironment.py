# ======================
# SpreadsEnvironment Class
#
# For representing a Spread Betting trading platform
# ======================

from tradeframework.api import TradeEnvironment
from tradeframework.engines import BaselineEngine
from tradeframework.tx import SpreadsTxMgr
import copy as cp


class SandboxEnvironment(TradeEnvironment):

    def __init__(self, name):
        TradeEnvironment.__init__(self, name)
        self.tradeEngine = BaselineEngine("Sandbox Engine", SpreadsTxMgr())

    def append(self, asset, copy=False):
        TradeEnvironment.append(self, asset)
        # Mediate between our Portfolio and the Environment
        portfolio = self.portfolio
        if copy:
            portfolio = cp.deepcopy(self.portfolio)
        return portfolio.append(asset)
