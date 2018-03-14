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

	def handleData(self, context, assetInfo):
		# Mediate between our Portfolio and the Environment
		return self.portfolio.handleData(context, assetInfo)

