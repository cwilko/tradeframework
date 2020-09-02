from tradeframework.api import Optimizer
import tradeframework.utils.trader as tradeUtils

import numpy as np
import pandas as pd


class KellyOptimizer(Optimizer):

    def __init__(self, name, env, window=0, weight=1.0):
        Optimizer.__init__(self, name, env)
        self.window = window
        self.weight = weight
        return

    def getWeights(self, context, returns):
        pReturns = np.array([tradeUtils.getPeriodReturns(ret).values.flatten() for ret in returns])

        if (self.window is None):
            F = self.getKellyWeights(pReturns)
            F = F.reshape(len(F), 1).repeat(len(pReturns[0]), axis=1)
        else:
            if ((pReturns.shape[1] > self.window) | (self.window == 0)):
                F_zero = np.zeros((len(pReturns), self.window))
                if (self.window == 0):
                    F = np.append(F_zero, np.array([self.getKellyWeights(pReturns[:, :i]) for i in range(self.window + 1, pReturns.shape[1] + 1)]).T, axis=1)
                else:
                    F = np.append(F_zero, np.array([self.getKellyWeights(pReturns[:, (i - (self.window + 1)):i]) for i in range(self.window + 1, pReturns.shape[1] + 1)]).T, axis=1)

                # Avoid lookahead by shifting the weights by a period.
                F[:, -1] = 0
                F = np.roll(F, 1)  # TODO : Use the roll to apply lookahead if needed.
            else:
                F = np.zeros(pReturns.shape)

        # Scale kelly values by scalar
        F = F * self.weight

        return [pd.DataFrame(np.array([assetWeight, assetWeight]).T, index=returns[0].index, columns=returns[0].columns) for assetWeight in F]

    @staticmethod
    def getKellyWeights(returns):

        # 1) Remove 0 rows from calculations, 2) Check for one-dimensional arrays, 3) Check for empty arrays (return zero array)
        # TODO : If multiple returns are identical (same M & V), consolidate them and equally portion out the resulting weight
        F = np.zeros(len(returns))
        mask = ~(returns == 0).all(axis=1)
        returns = returns[mask]
        activeReturns = len(returns)

        if ((activeReturns > 0) & (returns.shape[1] > 1)):
            if (activeReturns == 1):
                F[mask] = np.mean(returns) / np.var(returns, ddof=1)
            else:
                # Kelly Optimal weighting matrix
                M = np.mean(returns, axis=1)
                C = np.cov(returns, ddof=1)
                F[mask] = np.linalg.inv(C).dot(M).flatten()

        return F.flatten()
