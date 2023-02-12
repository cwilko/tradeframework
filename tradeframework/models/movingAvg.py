import pandas as pd
import numpy as np

import quantutils.core.timeseries as tsUtils
from tradeframework.api import Model


# Trade if price is higher/lower than MA

class MovingAverage(Model):

    def __init__(self, env, ma1_win):
        Model.__init__(self, env)
        self.window = ma1_win
        self.ma1_win = ma1_win
        return

    def getSignals(self, window, idx=0):

        ma = tsUtils.MA(window["Open"].values, self.ma1_win, self.ma1_win / 2)

        signals = np.nan_to_num(np.sign(window["Open"] - ma), 0)
        signals = pd.DataFrame(np.array([signals, signals]).T, window.index, columns=["bar", "gap"])

        return signals[idx:]
