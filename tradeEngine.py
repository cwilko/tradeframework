# ======================          
# TradeEngine Class
# ======================
import pandas as pd
class TradeEngine:

	BUY = 1
	CASH = 0
	SELL = -1
	
	def __init__(self, name, txMgr):
		self.name = name
		self.returns = pd.DataFrame(columns=[name])
		self.txMgr = txMgr
	
	def executeTrades(self, data, signals):
		pass

	def getReturns(self):
		return self.returns