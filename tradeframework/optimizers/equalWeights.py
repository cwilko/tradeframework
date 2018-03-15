from tradeframework.api import Optimizer
import numpy as np
import pandas as pd

class EqualWeightsOptimizer(Optimizer):

	def __init__(self, name, env):
		Optimizer.__init__(self, name, env)
		return

	def getWeights(self, context, returns):
		# Equal Weighting
		n = len(returns)
		F = np.ones(returns[0].shape) / n
		
		return [pd.DataFrame(F, index=returns[0].index, columns=returns[0].columns) for _ in returns]

		