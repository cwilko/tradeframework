import pandas as pd
import numpy as np
from tradeframework.api import Model

import quantutils.dataset.pipeline as ppl


class RetraceDailyMove(Model):

    def __init__(self, env, start="15:00", end="16:00"):
        Model.__init__(self, env)
        self.start = start
        self.end = end
        self.env
        return

    # Generate Signals and use them with asset values to calculate allocations
    # To be used only when cropped and only for a single period.
    # Will generate signal in the opposite direction (retrace) of the last 24 hrs (dailymove)
    def getSignals(self, window, idx=0):

        signals = pd.DataFrame(np.zeros((len(window), 2)), index=window.index, columns=["bar", "gap"])

        # Crop time
        scope = ppl.cropTime(window["Open"], self.start, self.end)

        sig = signals.loc[scope.index][1:]
        sig["bar"] = np.negative(np.sign(np.diff(scope)))
        signals.loc[sig.index] = sig

        return signals[idx:]
