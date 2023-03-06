# ======================
# SpreadsEnvironment Class
#
# For representing a Spread Betting trading platform
# ======================

from tradeframework.api.core import TradeEnvironment
from tradeframework.engines import BaselineEngine
from tradeframework.tx import SpreadsTxMgr


class SandboxEnvironment(TradeEnvironment):

    def __init__(self, name, tz="UTC"):
        TradeEnvironment.__init__(self, name, tz)
        self.tradeEngine = BaselineEngine("Sandbox Engine", SpreadsTxMgr())
