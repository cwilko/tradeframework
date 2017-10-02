# ======================          
# ZiplineEnvironment Class
#
# For integration with a Zipline framework
# ======================

from api import TradeEnvironment

class ZiplineEnvironment(TradeEnvironment):
	def __init__(self, name):
		TradeEnvironment.__init__(self, name)
		self.index = 0
		return

	def handleData(self, context, ts):
		# Mediate between our Portfolio and the Environment
		self.index += 1
		return self.portfolio.handleData(context, ts, self.index)

