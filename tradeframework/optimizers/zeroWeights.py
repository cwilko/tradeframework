from tradeframework.api.core import Optimizer
import numpy as np
import pandas as pd


class ZeroWeightsOptimizer(Optimizer):

    def __init__(self, env):
        Optimizer.__init__(self, env)
        return

    def getWeights(self, returns, idx=0):

        # Zero (null) Weighting
        F = np.zeros(returns[0][idx:].shape)

        return [pd.DataFrame(F, index=returns[0][idx:].index, columns=returns[0].columns) for _ in returns]
