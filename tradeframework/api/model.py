from . import Derivative, Asset


# ======================
# Model Class
# ======================


class Model(Derivative):

    BUY = 1
    CASH = 0
    SELL = -1

    def __init__(self, name, env):
        Derivative.__init__(self, name, env)

    def append(self, asset):
        # This only works if you have one asset, and only if the Model has Assets as children (rather than Derivatives)
        if (len(self.assets) > 0):
            self.assets[0].append(asset)
        else:
            self.assets = [asset]

        return super().append([self.getSignals(asset.values.index[0])], idx=asset.values.index[0])

    # Method for calculating the signals associated with input asset values
    def getSignals(self, asset):
        pass
