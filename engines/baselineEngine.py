# ======================          
# SpreadsEngine Class
# ======================
from api import TradeEngine
import pandas as pd

class BaselineEngine(TradeEngine):

	def _init_(self, name, txMgr):
		TradeEngine._init_(self, name, txMgr)

	def executeTrades(self, data, signals):

 		pd.set_option('precision',10)
		s1 = signals.iloc[:,::2]
		s2 = signals.iloc[:,1::2]
		s2.columns = s1.columns

		# Returns (Bar and Gap)
		barRet = s1.multiply((data.Close - data.Open ) / data.Open, axis=0) + 1
		gapRet = s2.multiply((data.Open.shift(-1) - data.Close) / data.Close, axis=0) + 1
		#print data[:110]
		#print pd.concat([data.Open, data.Close, data.Open.shift(-1), s1.multiply((data.Close - data.Open ) / data.Open, axis=0) + 1, s2.multiply((data.Open.shift(-1) - data.Close) / data.Close, axis=0) + 1], axis=1)[:110]

		
		# Transaction Costs		
		tx1 = s1.sub(s2.shift(1)).abs().multiply((0 / data.Open), axis=0) - 1 
		tx2 = s2.sub(s1).abs().multiply((0 / data.Close), axis=0) - 1
	
		# Total Returns
		#newReturns = barRet.multiply(tx1, axis=0).multiply(gapRet,axis=0).multiply(tx2, axis=0).prod(axis=1).to_frame()
		#newReturns = barRet.multiply(gapRet,axis=0).prod(axis=1).to_frame()
		newReturns = barRet.multiply(gapRet,axis=0)

		newReturns.columns = self.returns.columns
		#print newReturns[:110]
		self.returns = pd.concat([self.returns, newReturns], join="outer", axis=0)

		#print self.returns
		return self.returns
