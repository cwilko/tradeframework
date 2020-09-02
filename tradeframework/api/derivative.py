# ======================
# Strategy Class
# ======================

class Derivative:

    def __init__(self, name, env):
        self.name = name
        self.env = env

    def getName(self):
        return self.name

    def handleData(self, context, assetInfo):
        pass

    def getDerivativeInfo(self, context, assetInfos, weights):
        # Get allocations from TradeEngine
        derivInfo = self.env.tradeEngine.getDerivativeInfo(
            self.name, assetInfos, weights)

        # Update context
        if self.name not in context:
            context[self.name] = {}
        context[self.name]['dInfo'] = derivInfo

        return derivInfo
