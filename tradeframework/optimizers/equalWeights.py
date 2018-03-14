from tradeframework.api import Optimizer

class EqualWeightsOptimizer(Optimizer):

	def __init__(self, name, env):
		Optimizer.__init__(self, name, env)
		return

	def getWeights(self, context, returns):
		# Equal Weighting
		n = len(returns)
		F = [(1.0/n)] * n
		return F
		print F