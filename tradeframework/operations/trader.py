import numpy as np
import pandas as pd
import math

import quantutils.core.statistics as stats
import matplotlib
import matplotlib.pyplot as plt
#from matplotlib.dates import DateFormatter, WeekdayLocator, MonthLocator, DayLocator, MONDAY, AutoDateLocator, AutoDateFormatter
from matplotlib.dates import AutoDateLocator, AutoDateFormatter

import warnings
import pyfolio
from IPython.display import display


# Helper method to pretty print derviative performance


def plot(derivative, baseline=None, log=False, includeComponents=False, includePrimary=True, custom=[]):

    assets = []

    # Add component asset returns
    if (includeComponents):
        assets = derivative.assets[:]

    # Add primary returns
    if (includePrimary):
        assets.append(derivative)

    # Add baseline
    if (baseline is not None):
        assets.append(baseline)

    for userdata in custom:
        assets.append(userdata)

    if (log):
        pnl = lambda x: np.cumsum(np.log((getPeriodReturns(x.returns) + 1).resample('B').agg('prod')))
    else:
        pnl = lambda x: np.cumprod((getPeriodReturns(x.returns) + 1).resample('B').agg('prod'))

    # quarters = MonthLocator([1, 3, 6, 9])
    # allmonths = MonthLocator()
    # mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    # alldays = DayLocator()              # minor ticks on the days
    # weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    auto_locator = AutoDateLocator()
    auto_formatter = AutoDateFormatter(auto_locator)

    matplotlib.rcParams['figure.figsize'] = (12.0, 6.0)
    plt.ion()
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    ax.xaxis.set_major_locator(auto_locator)
    # ax.xaxis.set_minor_locator(allmonths)
    ax.xaxis.set_major_formatter(auto_formatter)

    for asset in assets:
        ax.plot(pnl(asset), label=asset.name)

    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.title("Derivative performance")
    plt.legend(loc='best')
    fig.canvas.draw()
    return fig, ax


def displaySummary(derivative, tInfo, baseline=None, log=False, includeComponents=True, includePrimary=True, full=True):
    print("Derivative name : " + derivative.name)
    print("Number of assets : " + str(len(derivative.assets)))
    if (baseline is not None):
        print("Baseline name : " + baseline.name)

    # Summary plot
    plot(derivative, baseline, log, includeComponents, includePrimary)

    # Show sample of trades
    pd.set_option('display.max_rows', 10)
    display(tInfo)

    if (baseline is not None):
        # Show local statistics
        stats.merton(derivative.returns["Open"][derivative.returns["Open"] != 0], baseline.returns["Open"][baseline.returns["Open"] != 0], display=True)

    if(full):
        # Show generic statistics
        warnings.filterwarnings('ignore')
        pyfolio.create_returns_tear_sheet(getPeriodReturns(derivative.returns))

# Helper method to turn derivative signals into trading information (buy/sell amounts, capital, etc)


def getTradingInfo(derivative, startCapital=1, unitAllocations=True, summary=True):
    ua = derivative.getUnderlyingAllocations()  # * startCapital * derivative.values.values
    if not unitAllocations:
        ua = ua * startCapital * derivative.values.values
    returns = pd.DataFrame(derivative.values.values, index=derivative.values.index, columns=[
                           ["Capital", "Capital"], derivative.values.columns])
    results = [returns * startCapital]
    mkts = list(set(ua.columns.get_level_values(0)))

    for l1 in mkts:
        a = ua[l1].values.flatten()
        b = np.roll(a, 1)
        b[0] = 0
        trade = pd.DataFrame(
            (a - b).reshape(len(derivative.values), 2), index=ua[l1].index, columns=ua[l1].columns)
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
    print("Time: %s" % row.index[0].isoformat())
    print("Portfolio Value: $%.4f" % currentValue)
    print("Capital: $%.2f" % capital)
    print("Target: %s" % target)

    for market in markets:
        print("====================")
        print("Market: %s" % market)
        price = row[market]["Price"].values.flatten()[idx]
        trade = row[market]["Trade"].values.flatten()[idx]
        signal = np.sign(trade)
        print("Price: $%.2f" % price)
        print("Signal: %s" % getSignal(signal))
        print("Amount: $%.2f" % np.abs(trade * capital))
        print()

    return row


# Given a next price value (or a list of possible prices), what would be the generated signal
def predictSignal(env, prices, capital=1):
    if not isinstance(prices, list):
        prices = [prices]

    for price in prices:
        getCurrentSignal(env.append(price, copy=True), capital)
