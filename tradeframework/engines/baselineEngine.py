# ======================
# SpreadsEngine Class
# ======================
from tradeframework.api import TradeEngine
import pandas as pd
import numpy as np


class BaselineEngine(TradeEngine):

    def _init_(self, name, txMgr):
        TradeEngine._init_(self, name, txMgr)
        pd.set_option('precision', 10)

    # Calculate portfolio returns
    # f(Pout, A) => R
    # R1 = P1(A2 - A1) / D1
    def calculateReturns(self, derivative, idx=0):

        dValues = derivative.values[idx:][["Open", "Close"]]
        flatValues = dValues.values.flatten()
        # Bootstrap with any existing derivative info.
        loc = -1
        if (idx != 0):
            loc = derivative.values.index.get_loc(idx) - 1

        if (loc >= 0):  # Not first index, therefore bootstrap from derivative
            flatValues = np.insert(flatValues, 0, derivative.values.iloc[loc]["Close"])
        else:
            # Bootstrap dummy values for new derivative
            flatValues = np.insert(flatValues, 0, derivative.values.iloc[0]["Open"])

        # Returns (Bar and Gap)
        returns = np.diff(flatValues) / flatValues[:-1]

        # Transaction Costs
        # tx1 = s1.sub(s2.shift(1)).abs().multiply((0 / data.Open), axis=0) - 1
        # tx2 = s2.sub(s1).abs().multiply((0 / data.Close), axis=0) - 1
        dReturns = pd.DataFrame(returns.reshape(dValues.shape), index=dValues.index, columns=['Open', 'Close'])

        return dReturns

    # f(Pin,A) => Pout, D
    # TODO : Deal with updates after an Open but before Close.
    def updateDerivative(self, derivative, assets, assetWeights, idx=0):

        assetValues = np.array([asset.values[idx:][['Open', 'Close']].values.flatten() for asset in assets]).T
        weights = np.array([weights.values.flatten() for weights in assetWeights]).T
        noOfValues = len(assetValues)

        # Bootstrap with any existing derivative info.

        loc = -1
        if (idx != 0):
            loc = assets[0].values.index.get_loc(idx) - 1

        if (loc >= 0):  # Not first index of our asset, therefore bootstrap from derivative
            assetValues = np.insert(assetValues, 0, [asset.values.iloc[loc]["Close"] for asset in assets], axis=0)
            dValues = [derivative.values.iloc[loc]["Close"]]
            allocations = [[derivative.uAllocations.iloc[loc][asset.name]["gap"].tolist() for asset in assets]]
        else:
            # Bootstrap dummy values for new derivative
            assetValues = np.insert(assetValues, 0, np.zeros(len(assets)), axis=0)
            dValues = [1]
            allocations = [np.zeros(len(assets))]

        # Iterate over table. Construct deriviative value and relevant allocation.
        # (ref: Short Sell and Hold phenomenon)
        for i in range(1, noOfValues + 1):
            # TODO : Add Rebalancing support. Currently rebalance on every bar & gap.

            dValues.append(dValues[i - 1] + sum(allocations[i - 1] * (assetValues[i] - assetValues[i - 1])))
            allocations.append(weights[i - 1] * dValues[i] / assetValues[i])

        # m x n x 2 matrices
        columns = pd.MultiIndex.from_product([[asset.name for asset in assets], ["bar", "gap"]])
        dAllocations = pd.DataFrame(np.hstack([x.reshape(len(assetWeights[0]), 2) for x in np.array(allocations[1:]).T]), index=assetWeights[0].index, columns=columns)
        # TODO: Why are we wrapping up weights again, just return original weights? or not at all?
        dWeights = pd.DataFrame(np.hstack([x.reshape(len(assetWeights[0]), 2) for x in np.array(weights).T]), index=assetWeights[0].index, columns=columns)

        # n x 2 matrices
        dReturns = np.diff(dValues) / dValues[:-1]
        dReturns = pd.DataFrame(np.array(dReturns).reshape(assetWeights[0].shape), index=assetWeights[0].index, columns=['Open', 'Close'])

        dValues = pd.DataFrame(np.array(dValues[1:]).reshape(assetWeights[0].shape), index=assetWeights[0].index, columns=['Open', 'Close']) \
            .assign(High=lambda x: x[["Open", "Close"]].max(axis=1)) \
            .assign(Low=lambda x: x[["Open", "Close"]].min(axis=1)) \
            [["Open", "High", "Low", "Close"]]

        print(dAllocations)
        return [dValues, dAllocations, dWeights, dReturns]
