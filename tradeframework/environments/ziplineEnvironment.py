# ======================
# ZiplineEnvironment Class
#
# For integration with a Zipline framework
# ======================

from tradeframework.api.core import TradeEnvironment


class ZiplineEnvironment(TradeEnvironment):

    def __init__(self, name, tz):
        TradeEnvironment.__init__(self, name, tz)
        return
