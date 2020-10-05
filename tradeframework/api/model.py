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


def append_asset(func):
    def wrapper(self, asset):
        # This only works if you have one asset, and only if the Model has Assets as children (rather than Derivatives)
        if (len(self.assets) > 0):
            asset = self.assets[0].append(asset)
        return func(self, asset)
    return wrapper
