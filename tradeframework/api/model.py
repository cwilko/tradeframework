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
        self.window = 0  # Default - No window
        self.assetMap = {}

    # TODO: This only works if you have one asset, and only if the Model has Assets as children (rather than Derivatives)
    def append(self, asset):
        storedAsset = self.env.getAssetStore().append(asset)
        self.assetMap[asset.getName()] = storedAsset
        self.assets = list(self.assetMap.values())
        self.weightedAssets = list(self.assetMap.values())

        signals = [self.getSignals(asset.values.index[0]) for asset in self.assets]

        return super().updateState(signals, idx=asset.values.index[0])

    # Method for calculating the signals associated with input asset values
    def getSignals(self, asset):
        pass

    # TODO: Support multiple assets, e.g. getWindow(self, assetName, idx)
    def getWindow(self, idx):

        if (self.window is -1):  # Use all available data
            idx = 0
        elif (idx is not 0):
            idx = self.assets[0].values.index.get_loc(idx)
            idx = max(0, idx - self.window)

        return self.assets[0].values[idx:]
