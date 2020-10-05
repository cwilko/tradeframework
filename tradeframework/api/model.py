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

    def append(self, asset):
        # This only works if you have one asset, and only if the Model has Assets as children (rather than Derivative)
        if (len(self.assets) > 0):
            self.assets[0].append(asset)
        else:
            self.assets = [asset]

        # TODO pass a window rather than all asset data
        return self.update(self.assets, [self.getSignals(self.assets[0])])

    # Method for calculating the signals associated with input asset values
    def getSignals(self, asset):
        pass
