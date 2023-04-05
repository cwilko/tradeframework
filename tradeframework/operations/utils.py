from tradeframework.api.core import Asset
import pandas as pd
import numpy as np

# Helper method to merge bar and gap returns into a single period


def getPeriodReturns(returns):
    return pd.DataFrame((returns + 1).prod(axis=1) - 1, columns=["period"])


def getPeriodLogReturns(returns):
    return pd.DataFrame(np.log(returns + 1).sum(axis=1), columns=["period"])


def getTradedReturns(returns):
    return returns.loc[(returns != 0).any(axis=1)]


def getTradedLogReturns(returns):
    return np.log(returns.loc[(returns != 0).any(axis=1)] + 1)


def createAssetFromOHLC(index, ohlc, name="OHLCData"):
    return Asset(
        name, pd.DataFrame(ohlc, index=index, columns=["Open", "High", "Low", "Close"])
    )
