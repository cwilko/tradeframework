# ======================          
# SpreadsEngine Class
# ======================
from tradeframework.api import TradeEngine, DerivativeInfo
import pandas as pd
import numpy as np

class BaselineEngine(TradeEngine):

	def _init_(self, name, txMgr):
		TradeEngine._init_(self, name, txMgr)

	# Calculate portfolio returns
	# f(Pout, A) => R
	# R1 = P1(A2 - A1) / D1
	def getReturns(self, assetValues):

		assetValues_flat = assetValues[['Open','Close']].values.flatten()

 		pd.set_option('precision',10)
		#s1 = allocations.iloc[:,::2]
		#s2 = allocations.iloc[:,1::2]
		#s2.columns = s1.columns

		# Returns (Bar and Gap)
		returns_flat = np.diff(assetValues_flat) / assetValues_flat[:-1]
		returns_flat = np.append(returns_flat,0)
		
		# Transaction Costs		
		#tx1 = s1.sub(s2.shift(1)).abs().multiply((0 / data.Open), axis=0) - 1 
		#tx2 = s2.sub(s1).abs().multiply((0 / data.Close), axis=0) - 1
	
		# Concatenate with history
		#self.returns = pd.concat([self.returns, newReturns], join="outer", axis=0)

		# Unravel
		returns = pd.DataFrame((returns_flat.reshape(assetValues.shape)), index=assetValues.index, columns=assetValues.columns)

		return returns

	# f(Pin,A) => Pout, D
	def getDerivativeInfo(self, name, assetInfos, assetWeights):
	
		# Iterate over table. Construct deriviative value and relevant allocation.
		# (ref: Short Sell and Hold phenomenon)
		assetValues = np.array([assetInfo.values[['Open','Close']].values.flatten() for assetInfo in assetInfos]).T
		weights = np.array([weights.values.flatten() for weights in assetWeights]).T
		noOfValues = len(assetValues)
		dValues = [1]
		allocations = []
		for i in range(1, noOfValues):
			# TODO : Add Rebalancing support. Currently rebalance on every bar & gap.
			allocations.append(weights[i-1] * dValues[i-1] / assetValues[i-1])
			dValues.append(dValues[i-1] + sum(allocations[i-1] * (assetValues[i] - assetValues[i-1])))

		allocations.append(weights[i-1] * dValues[i-1] / assetValues[i-1]) # Used in online "mode" for next time we call this

		# m x n x 2 matrices
		columns = pd.MultiIndex.from_product([[assetInfo.name for assetInfo in assetInfos], ["bar","gap"]])
		dAllocations = pd.DataFrame(np.hstack([x.reshape(len(assetWeights[0]),2) for x in np.array(allocations).T]), index = assetWeights[0].index, columns=columns)
		dWeights = pd.DataFrame(np.hstack([x.reshape(len(assetWeights[0]),2) for x in np.array(weights).T]), index = assetWeights[0].index, columns=columns)
		
		# n x 2 matrices
		dValues = pd.DataFrame(np.array(dValues).reshape(assetWeights[0].shape), index = assetWeights[0].index, columns=['Open', 'Close'])
		dReturns = self.getReturns(dValues)

		return DerivativeInfo(name, dValues, dAllocations, dWeights, dReturns, assetInfos)

