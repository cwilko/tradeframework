# ======================
# TradeEngine Class
# ======================


class TradeEngine:

    BUY = 1
    CASH = 0
    SELL = -1

    def __init__(self, name, txMgr):
        self.name = name
        self.txMgr = txMgr

    # f(Pin, A) => R
    def calculateReturns(self, assetValues, allocations):
        pass

    # f(Pin,A) => Pout
    def createDerivative(self, asset, weights):
        pass
