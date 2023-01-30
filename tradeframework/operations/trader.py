import numpy as np
import pandas as pd
import math

# Helper method to turn derivative signals into trading information (buy/sell amounts, capital, etc)


def getTradingInfo(derivative, startCapital=1, unitAllocations=True, summary=True):
    ocData = derivative.values[["Open", "Close"]]
    ua = derivative.getUnderlyingAllocations()  # * startCapital * derivative.values.values
    if not unitAllocations:
        ua = ua * startCapital * ocData.values
    returns = pd.DataFrame(ocData.values, index=ocData.index, columns=[["Capital", "Capital"], ocData.columns])
    results = [returns * startCapital]
    mkts = list(set(ua.columns.get_level_values(0)))

    for l1 in mkts:
        a = ua[l1].values.flatten()
        b = np.roll(a, 1)
        b[0] = 0
        trade = pd.DataFrame(
            (a - b).reshape(len(ocData), 2), index=ua[l1].index, columns=ua[l1].columns)
        prices = pd.DataFrame(
            derivative.env.getAssetStore().getAsset("DOW").values[["Open", "Close"]].values, index=ua[l1].index, columns=["Open", "Close"])
        results.append(pd.concat([prices, ua[l1], trade], keys=[
                       "Price", "Allocation", "Trade"], axis=1))

    mkts.insert(0, derivative.name)
    results = pd.concat(results, keys=mkts, axis=1)

    # Filter out non-trading periods if summary needed
    if (summary):
        idx = pd.IndexSlice
        results = results[(results.loc[:, idx[:, :, ['bar', 'gap']]] != 0).any(axis=1)]

    return results


def getSignal(x):
    if x == 0:
        return "HOLD"
    if x > 0:
        return "BUY"
    else:
        return "SELL"

# Get the signal associated with the most recent prices in the tradingInfo structure


def getCurrentSignal(portfolio, capital=1):
    tradingInfo = getTradingInfo(portfolio, summary=False)
    idx = 0
    target = "OPEN"
    if not math.isnan(tradingInfo[-1:].values.flatten()[-1]):
        idx = 1
        target = "CLOSE"

    row = tradingInfo[-1:]  # Get last seen row of table
    markets = row.columns.levels[0].values[1:]
    value = row[row.columns.levels[0][0]]["Capital"].values.flatten()  # Get last seen value of capital
    currentValue = value[idx]

    currentSignal = {
        "timestamp": row.index[0].isoformat(),
        "value": currentValue,
        "capital": capital,
        "target": target,
        "markets": []
    }

    for market in markets:

        price = row[market]["Price"].values.flatten()[idx]
        trade = row[market]["Trade"].values.flatten()[idx]
        signal = np.sign(trade)

        marketSignal = {
            "name": market,
            "price": price,
            "signal": getSignal(signal),
            "amount": np.abs(trade * capital)
        }

        currentSignal["markets"].append(marketSignal)

    return currentSignal


def printSignals(signals):

    if not isinstance(signals, list):
        signals = [signals]

    for signal in signals:
        print("Time: %s" % signal["timestamp"])
        print("Portfolio Value: $%.4f" % signal["value"])
        print("Capital: $%.2f" % signal["capital"])
        print("Target: %s" % signal["target"])

        for market in signal["markets"]:
            print("====================")
            print("Market: %s" % market["name"])
            print("Price: $%.2f" % market["price"])
            print("Signal: %s" % market["signal"])
            print("Amount: $%.2f" % market["amount"])
            print()

# Given a next price value (or a list of possible prices), what would be the generated signal


def predictSignals(env, prices, capital=1):
    if not isinstance(prices, list):
        prices = [prices]

    return [getCurrentSignal(env.append(price, copy=True), capital) for price in prices]
