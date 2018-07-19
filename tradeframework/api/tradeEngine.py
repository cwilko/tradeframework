# ======================          
# TradeEngine Class
# ======================

import numpy as np
import pandas as pd

class TradeEngine:

	BUY = 1
	CASH = 0
	SELL = -1
	
	def __init__(self, name, txMgr):
		self.name = name
		self.txMgr = txMgr
	
	def executeTrades(self, data, signals):
		pass

	# f(Pin, A) => R
	def getReturns(self, assetValues, allocations):
		pass

	# f(Pin,A) => Pout
	def getDerivativeInfo(self, assetInfo, weights):
		pass


	# f(Pin,A) => Pout
	def getDerivativeValues(self, assetValues, allocations):
		pass
    
	def getTradingInfo(self, dInfo, startCapital=1):
	    ua = dInfo.getUnderlyingAllocations() * startCapital
	    returns = pd.DataFrame(dInfo.values.values, index=dInfo.values.index, columns=[["Capital","Capital"],dInfo.values.columns])
	    results = [returns * startCapital]
	    mkts = list(set(ua.columns.get_level_values(0)))

	    for l1 in mkts:
	        a = ua[l1].values.flatten()
	        b = np.roll(a,1)
	        b[0]=0
	        trade = pd.DataFrame((a - b).reshape(len(dInfo.values),2), index=ua[l1].index, columns=ua[l1].columns)
	        results.append(pd.concat([ua[l1], trade],keys=["Allocation", "Trade"], axis=1))

	    mkts.insert(0,dInfo.name)
	    results = pd.concat(results, keys=mkts, axis=1)
	    
	    # Filter out non-trading periods
	    idx = pd.IndexSlice
	    return results[(results.loc[:,idx[:,:,['bar','gap']]]!=0).any(axis=1)]

class AssetInfo:
	def __init__(self, name, values):
		self.name = name
		self.values = values

	def getUnderlyingAllocations(self):
		return pd.DataFrame(np.ones((len(self.values),2)), columns=[[self.name, self.name],['bar','gap']], index=self.values.index)
		
class DerivativeInfo(AssetInfo):
	def __init__(self, name, values, allocations, weights, returns, childAssets):
		AssetInfo.__init__(self, name, values)
		self.allocations = allocations	
		self.weights = weights
		self.returns = returns
		self.assets = childAssets

	def getUnderlyingAllocations(self):
	    myUAllocations = None
	    assetCount = len(self.allocations.columns.levels[0])
	    for l1 in range(assetCount):
	        uAllocations = self.assets[l1].getUnderlyingAllocations()
	        for l2 in uAllocations.columns.levels[0]:
	            assetUAllocation = uAllocations[l2] * self.allocations[self.allocations.columns.levels[0][l1]].values
	            if (myUAllocations is None):
	                myUAllocations = pd.DataFrame(assetUAllocation.values, index=assetUAllocation.index, columns=[[l2,l2],['bar','gap']])
	            elif (l2 in myUAllocations.columns.levels[0]):
	                myUAllocations[l2] += assetUAllocation
	            else:
	                myUAllocations = pd.concat([myUAllocations, assetUAllocation], axis=1)
	    return myUAllocations