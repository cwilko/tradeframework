import pandas as pd
import numpy as np

import quantutils.core.timeseries as tsUtils
from tradeframework.api.core import Model


# Trade if price is higher/lower than MA

class MovingAverageResample(Model):

    def __init__(self, env, ma1_win, src_sample, tgt_sample):
        Model.__init__(self, env)
        self.window = ma1_win
        self.ma1_win = ma1_win
        self.src_sample = src_sample
        self.tgt_sample = tgt_sample
        return

    def getSignals(self, window, idx=0):

        resample = window.resample(self.tgt_sample, label="left", closed="left").apply({"Open": "first"}).dropna()
        ma = tsUtils.MA(resample["Open"].values, self.ma1_win, self.ma1_win / 2)

        resample_signals = np.nan_to_num(np.sign(resample["Open"] - ma), 0)
        resample_signals = pd.DataFrame(np.array([resample_signals, resample_signals]).T, resample.index, columns=["bar", "gap"])

        signals = resample_signals.resample(self.src_sample).ffill()
        signals = signals[signals.index.isin(window.index)]
        signals = signals.append(pd.DataFrame({"bar": resample_signals.iloc[-1]["bar"], "gap": resample_signals.iloc[-1]["gap"]}, index=window[window.index > signals.index[-1]].index))

        return signals[idx:]
