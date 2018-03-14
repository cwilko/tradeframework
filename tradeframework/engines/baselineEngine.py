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
	def getReturns(self, assetValues, allocations, dValues=None):

		if (dValues is None):
			dValues = self.getDerivativeValues(assetValues, allocations)

		assetValues_flat = assetValues[['Open','Close']].values.flatten()
		derivValues_flat = dValues.values.flatten()
		allocations_flat = allocations.values.flatten()

 		pd.set_option('precision',10)
		#s1 = allocations.iloc[:,::2]
		#s2 = allocations.iloc[:,1::2]
		#s2.columns = s1.columns

		# Returns (Bar and Gap)
		returns_flat = allocations_flat[:-1] * np.diff(assetValues_flat) / derivValues_flat[:-1]
		returns_flat = np.append(returns_flat, 0)
		
		# Transaction Costs		
		#tx1 = s1.sub(s2.shift(1)).abs().multiply((0 / data.Open), axis=0) - 1 
		#tx2 = s2.sub(s1).abs().multiply((0 / data.Close), axis=0) - 1
	
		# Concatenate with history
		#self.returns = pd.concat([self.returns, newReturns], join="outer", axis=0)

		# Unravel
		#returns = pd.DataFrame((returns_flat.reshape(allocations.shape) + 1).prod(axis=1)-1, index=allocations.index, columns=["period"])
		returns = pd.DataFrame((returns_flat.reshape(allocations.shape)), index=allocations.index, columns=allocations.columns)

		return returns

	# TODO : Cope with assetValues and weights as 3D matrices (lists of 2D matrices)
	# f(Pin,A) => Pout, D
	def getDerivativeInfo(self, name, assetValues, weights):
	
		# Iterate over table. Construct deriviative value and relevant allocation.
		# (ref: Short Sell and Hold phenomenon)

		assetValues_flat = assetValues[['Open','Close']].values.flatten()
		signals_flat = weights.values.flatten()
		dValues = [1]
		allocations = []
		for i in range(1, len(assetValues_flat)):
			# TODO : Add Rebalancing support. Currently rebalance on every bar & gap.
			allocations.append(signals_flat[i-1] * dValues[i-1] / assetValues_flat[i-1])
			dValues.append(dValues[i-1] + (allocations[i-1] * (assetValues_flat[i] - assetValues_flat[i-1])))

		allocations.append(signals_flat[i-1] * dValues[i-1] / assetValues_flat[i-1]) # TODO : Check this

		dAllocations = pd.DataFrame(np.array(allocations).reshape(weights.shape), index = weights.index, columns=['bar', 'gap'])
		dValues = pd.DataFrame(np.array(dValues).reshape(weights.shape), index = weights.index, columns=['Open', 'Close'])
		dReturns = self.getReturns(assetValues, dAllocations, dValues)

		return DerivativeInfo(name, dValues, dAllocations, weights, dReturns)


	# f(Pin,A) => Pout, D
	def getDerivativeValues(self, assetValues, allocations):
	
		# Iterate over allocations. Construct deriviative value.
		# (ref: Short Sell and Hold phenomenon)

		assetValues_flat = assetValues[['Open','Close']].values.flatten()
		allocations_flat = allocations.values.flatten()
		dValues = [1]
		for i in range(1, len(assetValues_flat)):
			dValues.append(dValues[i-1] + (allocations_flat[i-1] * (assetValues_flat[i] - assetValues_flat[i-1])))

		dValues = np.array(dValues).reshape(allocations.shape)

		dValues = pd.DataFrame(dValues, index = allocations.index, columns=['Open', 'Close'])

		return dValues
