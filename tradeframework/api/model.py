from . import WeightGenerator

# ======================
# Model Class
# ======================


class Model(WeightGenerator):

    BUY = 1
    CASH = 0
    SELL = -1

    def __init__(self, env, window=0):
        self.window = window  # Default - No window
        self.env = env

    # Method for calculating the signals associated with input asset values
    def generateWeights(self, derivatives, idx):
        return [self.getSignals(self.getWindow(derivative, idx), idx) for derivative in derivatives]

    def getWindow(self, derivative, idx):

        if (self.window is -1):  # Use all available data
            idx = 0
        elif (idx is not 0):
            idx = derivative.values.index.get_loc(idx)
            idx = max(0, idx - self.window)

        return derivative.values[idx:]
