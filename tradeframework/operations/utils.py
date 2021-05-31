from tradeframework.api import Asset
import pandas as pd

# Helper method to merge bar and gap returns into a single period


def getPeriodReturns(returns):
    returns = (returns + 1).prod(axis=1) - 1
    returns.columns = ["period"]
    return returns


def createAssetFromOHLC(index, ohlc, name="OHLCData"):
    return Asset(name, pd.DataFrame(ohlc, index=index, columns=["Open", "High", "Low", "Close"]))
