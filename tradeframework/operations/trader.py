import numpy as np
import pandas as pd
import math

# Helper method to turn derivative signals into trading information (buy/sell amounts, capital, etc)


def getTradingInfo(derivative, startCapital=1, unitAllocations=True, summary=True):
    ocData = derivative.values[["Open", "Close"]]
    ua = getUnderlyingAllocations(derivative)  # * startCapital * derivative.values.values
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
            np.round((a - b), 8).reshape(len(ocData), 2), index=ua[l1].index, columns=ua[l1].columns)
        prices = pd.DataFrame(
            derivative.env.getAssetStore().getAsset(l1).values[["Open", "Close"]].values, index=ua[l1].index, columns=["Open", "Close"])
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


def getCurrentSignal(derivative, capital=1, target=None, filter=[]):
    tradingInfo = getTradingInfo(derivative, summary=False)
    idx = 0
    if not target:
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

        if not filter or marketSignal["signal"] in filter:
            currentSignal["markets"].append(marketSignal)

    if not currentSignal["markets"]:
        currentSignal = None

    return currentSignal


def printSignals(signals):

    if not isinstance(signals, list):
        signals = [signals]

    for signal in signals:
        print("====================")
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


def predictSignals(derivative, prices, underlying=False, capital=1, target=None, filter=[]):
    if not isinstance(prices, list):
        prices = [prices]

    signals = []
    for price in prices:
        envCopy = derivative.env.copy()
        envCopy.append(price, refreshPortfolio=True)
        derivative = envCopy.findAsset(derivative.getName())
        derivatives = [derivative]
        if underlying:
            derivatives = derivative.weightedAssets
        dSignals = [getCurrentSignal(d, capital=capital, target=target, filter=filter) for d in derivatives]
        signals.append(dSignals)

    return signals

# Shows the allocation to the underlying assets (leaf nodes) at each time period


def getUnderlyingAllocations(derivative):

    currentAllocations = derivative.getAllocations()

    myUAllocations = None
    if (currentAllocations is not None):
        # Derivative
        for l1 in derivative.weightedAssets:
            uAllocations = getUnderlyingAllocations(l1)
            for l2 in uAllocations.columns.levels[0]:
                assetUAllocation = uAllocations[l2] * currentAllocations[l1.getName()].values
                if (myUAllocations is None):
                    myUAllocations = pd.DataFrame(
                        assetUAllocation.values, index=assetUAllocation.index, columns=[[l2, l2], ['bar', 'gap']])
                elif (l2 in myUAllocations.columns.levels[0]):
                    myUAllocations[l2] += assetUAllocation
                else:
                    myUAllocations = pd.concat(
                        [myUAllocations, pd.DataFrame(assetUAllocation.values, index=assetUAllocation.index, columns=[[l2, l2], ['bar', 'gap']])], axis=1)

    else:
        # Asset
        myUAllocations = pd.DataFrame(
            np.ones((len(derivative.values), 2)),
            columns=[[derivative.name, derivative.name], ['bar', 'gap']],
            index=derivative.values.index
        )

    return myUAllocations
