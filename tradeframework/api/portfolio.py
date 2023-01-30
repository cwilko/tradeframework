from . import Derivative

# ======================
# Portfolio Class
# ======================


class Portfolio(Derivative):

    def __init__(self, name, env, optimizer=None):
        Derivative.__init__(self, name, env)
        if (optimizer is None):
            self.optimizer = env.createOptimizer(
                self.name, "EqualWeightsOptimizer")
        else:
            self.optimizer = optimizer

        self.assetCache = {}

    def addAsset(self, asset, weighted=True):
        self.assets.append(asset)
        self.assetCache[asset.getName()] = asset
        if weighted:
            self.weightedAssets.append(asset)
        return asset

    def findAsset(self, assetName):
        if assetName in self.assetCache:
            return self.assetCache[assetName]
        else:
            for asset in self.assets:
                foundAsset = asset.findAsset(assetName)
                if foundAsset is not None:
                    return foundAsset

        raise Exception('Error: Asset, {0}, found in portfolio {1}'.format(assetName, self.getName()))

    def append(self, asset):

        if not self.weightedAssets:
            raise Exception('Error: No appendable assets for portfolio: ', self.getName())

        # Update all children
        self.assets = [derivative.append(asset) for derivative in self.assets]

        # Calculate portfolio allocation
        weights = self.optimizer.getWeights([derivative.returns for derivative in self.weightedAssets], idx=asset.values.index[0])

        # Update derivative state
        return super().updateState(weights, idx=asset.values.index[0])
