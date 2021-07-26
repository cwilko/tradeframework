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

    def addAsset(self, asset):
        self.assets.append(asset)
        return asset

    def append(self, asset):

        # Update all children
        self.assets = [derivative.append(asset) for derivative in self.assets]

        # Calculate portfolio allocation
        weights = self.optimizer.getWeights([derivative.returns for derivative in self.assets], idx=asset.values.index[0])

        # Update derivative state
        return super().append(weights, idx=asset.values.index[0])
