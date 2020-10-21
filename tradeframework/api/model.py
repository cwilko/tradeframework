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
            idx = self.assets[0].values.index.get_loc(asset.values.index[0]) - 1
            window = Asset(asset.getName(), self.assets[0].values[idx:])
            latest_value = self.values.iloc[idx]["Open"]
        else:
            self.assets = [asset]
            window = asset
            latest_value = 1

        # TODO pass a window rather than all asset data

        return self.appendData([window], [self.getSignals(window)], latest_value)

    # Method for calculating the signals associated with input asset values
    def getSignals(self, asset):
        pass
