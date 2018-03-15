from tradeframework.api import Optimizer
from tradeframework.api import TradeEngine

import numpy as np
import pandas as pd

class KellyOptimizer(Optimizer):

	def __init__(self, name, env, window=0):
		Optimizer.__init__(self, name, env)
		self.window = window # TODO: n = window size, 0 = use all previous data, None = include future data (lookahead)
		return

	def getWeights(self, context, returns):
		pReturns = np.array([TradeEngine.getPeriodReturns(ret).values.flatten() for ret in returns])

		if (self.window is None):
			F = self.getKellyWeights(pReturns).T
		else:
			if ((pReturns.shape[1] > self.window) | (self.window == 0)):
				F_zero = np.zeros((len(pReturns),self.window))
				F = np.append(F_zero, np.array([self.getKellyWeights(pReturns[:,:i]) for i in range(self.window+1,pReturns.shape[1]+1)]).T, axis=1)

				# Avoid lookahead by shifting the weights by a period.
				F[:,-1] = 0
				np.roll(F,1)
			else:
				F = np.zeros(pReturns.shape)

		return [pd.DataFrame(np.array([[assetWeight, assetWeight]]).T, index=returns[0].index, columns=returns[0].columns) for assetWeight in F]

	@staticmethod	
	def getKellyWeights(returns):
		
		# 1) Remove 0 rows from calculations, 2) Check for one-dimensional arrays, 3) Check for empty arrays (return zero array)

		F = np.zeros(len(returns))
		mask = ~(returns==0).all(axis=1)
		returns = returns[mask]
		activeReturns = len(returns)

		if ((activeReturns>0) & (returns.shape[1]>1)):
			if (activeReturns == 1):
				F[mask] = np.mean(returns) / np.var(returns, ddof=1)
			else:
				# Kelly Optimal weighting matrix			
				M = np.array([returns.mean(axis=1)]).T
				C = np.cov(returns, ddof=1)
				F[mask] = np.linalg.inv(C).dot(M)

		return F.flatten()