from . import Derivative

# ======================          
# Model Class
# ======================

class Model(Derivative):

    BUY = 1
    CASH = 0
    SELL = -1

    def __init__(self, name, env):
        Derivative.__init__(self, name, env)
        
    def handleData(self, context, assetInfo):        
        return Derivative.handleData(self, context, assetInfo)
