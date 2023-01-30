import pandas as pd
import numpy as np

import quantutils.core.timeseries as tsUtils
from tradeframework.api import Model


# Trade if price is higher/lower than MA

class MovingAverageXOver(Model):

    def __init__(self, name, env, ma1_fast, ma2_slow):
        Model.__init__(self, name, env)
        self.window = max(ma1_fast, ma2_slow)
        self.ma1_fast = ma1_fast
        self.ma2_slow = ma2_slow
        return

    def getSignals(self, idx=0):

        window = self.getWindow(idx)

        ma_fast = tsUtils.MA(window["Open"].values, self.ma1_fast, self.ma1_fast / 2)
        ma_slow = tsUtils.MA(window["Open"].values, self.ma2_slow, self.ma2_slow / 2)

        signals = np.nan_to_num(np.sign(ma_fast - ma_slow), 0)
        signals = pd.DataFrame(np.array([signals, signals]).T, window.index, columns=["bar", "gap"])

        return signals[idx:]
