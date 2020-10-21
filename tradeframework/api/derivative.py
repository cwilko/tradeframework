from . import Asset
import pandas as pd

# ======================
# Derivative Class
# ======================


class Derivative(Asset):

    def __init__(self, name, env, values=None, uAllocations=None, weights=None, returns=None, assets=None):
        Asset.__init__(self, name, values)
        self.env = env
        self.uAllocations = uAllocations
        self.weights = weights
        self.returns = returns
        if (assets is None):
            self.assets = []
        else:
            self.assets = assets

    def append(self, weights, idx=0):

        values, uAllocations, weights, returns = self.env.tradeEngine.updateDerivative(self, self.assets, weights, idx)

        if self.values is None:
            self.values = values
            self.uAllocations = uAllocations
            self.weights = weights
            self.returns = returns
        else:
            self.values = values.combine_first(self.values)
            self.uAllocations = uAllocations.combine_first(self.uAllocations)
            self.weights = weights.combine_first(self.weights)
            self.returns = returns.combine_first(self.returns)

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
