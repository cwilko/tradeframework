from . import Asset
import pandas as pd

# ======================
# Derivative Class
# ======================


class Derivative(Asset):

    def __init__(self, name, env, values=pd.DataFrame(), uAllocations=None, weights=None, returns=pd.DataFrame(), assets=None, weightedAssets=None, weightGenerator=None):
        Asset.__init__(self, name, values=values, returns=returns, env=env)
        self.uAllocations = uAllocations
        self.weights = weights

        if (assets is None):
            self.assets = []
            self.weightedAssets = []
        else:
            self.assets = assets
            self.weightedAssets = weightedAssets

        if (weightGenerator is None):
            self.weightGenerator = env.createOptimizer("EqualWeightsOptimizer")
        else:
            self.weightGenerator = weightGenerator

        # Cache for asset searching
        self.assetCache = {}

    def __str__(self):
        return ''.join(['{ "id": "', self.uuid, '", "name": "', self.name, '", "type": "', str(type(self)), '", "assets": [', ','.join([str(asset) for asset in self.assets]), '] }'])

    def getAllocations(self):
        return self.uAllocations

    def getWeights(self):
        return self.weights

    def getReturns(self):
        return self.returns

    def getAsset(self, assetName):
        if assetName in self.assetCache:
            return self.assetCache[assetName]
        return None

    def addAsset(self, asset, weighted=True):
        self.assets.append(asset)
        if weighted:
            self.weightedAssets.append(asset)

        # Also add to search cache
        self.assetCache[asset.getName()] = asset

        return self

    def addStoredAsset(self, names):
        [self.addAsset(self.env.getAssetStore().getAsset(name)) for name in names]
        return self

    def findAsset(self, assetName):
        if assetName in self.assetCache:
            return self.assetCache[assetName]
        else:
            for asset in self.assets:
                foundAsset = asset.findAsset(assetName)
                if foundAsset is not None:
                    return foundAsset

        raise Exception('Error: Asset, {0}, not found in portfolio {1}'.format(assetName, self.getName()))

    def refresh(self, idx):

        if not self.weightedAssets:
            raise Exception('Error: No appendable assets for portfolio: ', self.getName())

        # Update all children
        [asset.refresh(idx) for asset in self.assets]

        # Calculate portfolio allocation
        weights = self.weightGenerator.generateWeights(self.weightedAssets, idx=idx)

        # Update derivative state
        return self.updateState(weights, idx=idx)

    def updateState(self, weights, idx=0):

        values, uAllocations, weights, returns = self.env.tradeEngine.updateDerivative(self, self.weightedAssets, weights, idx)

        if self.weights is None:
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
