import pandas as pd
import numpy as np

import quantutils.core.timeseries as tsUtils
from tradeframework.api.core import Model


class StochasticOscXOver(Model):

    def __init__(self, env, window, threshold=None):
        Model.__init__(self, env)
        self.window = window
        self.threshold = threshold
        return

    def getSignals(self, window, idx=0):

        self.st_osc = tsUtils.stoch_osc(window, self.window)

        signals = np.nan_to_num(np.sign(self.st_osc["%K"] - self.st_osc["%D"]), 0)
        if self.threshold:
            signals[((self.st_osc["%K"] > self.threshold)
                     & (self.st_osc["%K"] - self.st_osc["%D"] > 0))
                    | ((self.st_osc["%K"] < (100 - self.threshold))
                        & (self.st_osc["%K"] - self.st_osc["%D"] < 0))] = 0
        signals = np.roll(signals, 1)
        signals[0] = 0

        signals = pd.DataFrame(np.array([signals, signals]).T, window.index, columns=["bar", "gap"])
        return signals[idx:]


class StochasticOscResampleXOver(Model):

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
