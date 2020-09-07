from . import Asset
import pandas as pd

# ======================
# Derivative Class
# ======================


class Derivative(Asset):

    def __init__(self, name, env):
        Asset.__init__(self, name)
        self.env = env
        self.uAllocations = None
        self.weights = None
        self.returns = None
        self.assets = []

    def handleData(self, assetInfo):
        pass

    def update(self, assets, weights):
        # Update allocations using TradeEngine
        self.values, self.uAllocations, self.weights, self.returns, self.assets = \
            self.env.tradeEngine.updateDerivative(assets, weights)

        return self

    def getAllocations(self):
        return self.uAllocations

    def getWeights(self):
        return self.weights

    def getReturns(self):
        return self.returns

    def getAsset(self, assetName):
        for asset in self.assets:
            if asset.getName() == assetName:
                break
            else:
                asset = None
        return asset

    def getUnderlyingAllocations(self):
        myUAllocations = None
        if (self.uAllocations is not None):
            assetCount = len(self.uAllocations.columns.levels[0])
            for l1 in range(assetCount):
                print(self)
                print(self.assets)
                uAllocations = self.assets[l1].getUnderlyingAllocations()
                for l2 in uAllocations.columns.levels[0]:
                    assetUAllocation = uAllocations[l2] * \
                        self.uAllocations[
                        self.uAllocations.columns.levels[0][l1]].values
                    if (myUAllocations is None):
                        myUAllocations = pd.DataFrame(
                            assetUAllocation.values, index=assetUAllocation.index, columns=[[l2, l2], ['bar', 'gap']])
                    elif (l2 in myUAllocations.columns.levels[0]):
                        myUAllocations[l2] += assetUAllocation
                    else:
                        myUAllocations = pd.concat(
                            [myUAllocations, assetUAllocation], axis=1)
        return myUAllocations
