# ======================
# ZiplineEnvironment Class
#
# For integration with a Zipline framework
# ======================

from tradeframework.api import TradeEnvironment


class ZiplineEnvironment(TradeEnvironment):

    def __init__(self, name):
        TradeEnvironment.__init__(self, name)
        return

    def append(self, asset, copy=False):
        # Mediate between our Portfolio and the Environment
        return self.portfolio.append(asset)
