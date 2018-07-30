# ===========================     
# Spreads Transaction Manager
# ===========================

class SpreadsTxMgr():
    def _init_():
        pass

    def getTxCost(self, allocation, prevAllocation, price, ret=0):
        txCost = abs(allocation - prevAllocation) * 0.0 / price
        return txCost