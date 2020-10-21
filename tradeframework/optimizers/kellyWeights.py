from tradeframework.api import Optimizer
import tradeframework.utils.trader as tradeUtils

import numpy as np
import pandas as pd


class KellyOptimizer(Optimizer):

    # window = None -> Lookahead, use all available past/future data to calculate weights
    # window = 0 (default) -> Use all previous data to calculate a weight
    # window = N -> Use a window of N data points to calculate a weight
    def __init__(self, name, env, window=0, weight=1.0):
        Optimizer.__init__(self, name, env)
        self.window = window
        self.weight = weight
        return

    # TODO: Accept assets rather than returns?
    def getWeights(self, returns, idx=0):

        # Converge bar and gap into single periods
        pReturns = np.array([tradeUtils.getPeriodReturns(ret).values.flatten() for ret in returns])
        deltaReturns = np.array([tradeUtils.getPeriodReturns(ret[idx:]).values.flatten() for ret in returns])
        window_start = len(pReturns[0]) - len(deltaReturns[0])

        if (self.window is None):
            # TODO: need unittest for this
            F = self.getKellyWeights(pReturns)
            F = F.reshape(len(F), 1).repeat(len(pReturns[0][idx:]), axis=1)
        else:
            if ((pReturns.shape[1] > self.window) | (self.window == 0)):
                F_zero = np.zeros((len(deltaReturns), max(self.window - window_start, 0)))
                if (self.window == 0):
                    # TODO: Remove all the ones from the next two lines!!
                    F = np.append(F_zero, np.array([self.getKellyWeights(pReturns[:, :i]) for i in range(window_start, pReturns.shape[1])]).T, axis=1)
                else:
                    F = np.append(F_zero, np.array([self.getKellyWeights(pReturns[:, (i - self.window):i]) for i in range(max(window_start, self.window), pReturns.shape[1])]).T, axis=1)
            else:
                F = np.zeros(deltaReturns.shape)

        # Scale kelly values by scalar
        F = F * self.weight

        return [pd.DataFrame(np.array([assetWeight, assetWeight]).T, index=returns[0][idx:].index, columns=returns[0].columns) for assetWeight in F]

    def getKellyWeights(self, returns):

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
