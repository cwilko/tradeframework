from tradeframework.api import Optimizer
import numpy as np
import pandas as pd


class EqualWeightsOptimizer(Optimizer):

    def __init__(self, name, env, weight=1.0):
        Optimizer.__init__(self, name, env)
        self.weight = weight
        return

    def getWeights(self, returns, idx=0):

        # Equal Weighting
        n = len(returns)
        F = np.ones(returns[0][idx:].shape) / n
        F = F * self.weight

        return [pd.DataFrame(F, index=returns[0][idx:].index, columns=returns[0].columns) for _ in returns]
