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
        self.window = 0  # Default - No window

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

    def getWindow(self, idx):

        if (self.window is -1):  # Use all available data
            idx = 0
        elif (idx is not 0):
            idx = self.assets[0].values.index.get_loc(idx)
            idx = max(0, idx - self.window)

        return self.assets[0].values[idx:]
