import pandas as pd
import numpy as np

import quantutils.core.timeseries as tsUtils
from tradeframework.api import Model


# Trade if price is higher/lower than MA

class StochasticOscXOver(Model):

    def __init__(self, env, window, src_sample, tgt_sample, threshold=None):
        Model.__init__(self, env)
        self.window = window
        self.threshold = threshold
        self.src_sample = src_sample
        self.tgt_sample = tgt_sample
        return

    def getSignals(self, window, idx=0):

        resample = window.resample(self.tgt_sample, label="left", closed="left").apply({"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna()

        st_osc = tsUtils.stoch_osc(resample, self.window)

        print(st_osc)

        resample_signals = np.nan_to_num(np.sign(st_osc["%K"] - st_osc["%D"]), 0)
        if self.threshold:
            resample_signals[st_osc["%K"].between(self.threshold, 100 - self.threshold)] = 0
        resample_signals = np.roll(resample_signals, 1)
        resample_signals[0] = 0

        resample_signals = pd.DataFrame(np.array([resample_signals, resample_signals]).T, resample.index, columns=["bar", "gap"])

        signals = resample_signals.resample(self.src_sample).ffill()
        signals = signals[signals.index.isin(window.index)]
        signals = signals.append(pd.DataFrame({"bar": resample_signals.iloc[-1]["bar"], "gap": resample_signals.iloc[-1]["gap"]}, index=window[window.index > signals.index[-1]].index))

        return signals[idx:]
