import pandas as pd
import numpy as np
from tradeframework.api import Model

import quantutils.dataset.pipeline as ppl

class RetraceDailyMove(Model):
    def __init__(self, name, env, start=None, end=None):
        Model.__init__(self, name, env)
        self.start = start
        self.end = end
        self.env
        return
    
    def handleData(self, context, assetInfo):
        Model.handleData(self, context, assetInfo)
        
        signals = pd.DataFrame(np.zeros((len(assetInfo.values), 2)), index=assetInfo.values.index, columns=["bar","gap"])

        if (self.start is not None):
            scope = ppl.cropTime(assetInfo.values["Open"], self.start, self.end)
        else:
            scope = assetInfo.values["Open"]
            
        sig = signals.loc[scope.index][1:]
        sig["bar"] = np.negative(np.sign(np.diff(scope)))
        signals.loc[sig.index] = sig

        return self.getDerivativeInfo(context, [assetInfo], [signals])