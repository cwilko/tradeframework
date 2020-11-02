import numpy as np
import pandas as pd

import quantutils.core.statistics as stats
import matplotlib
import matplotlib.pyplot as plt
#from matplotlib.dates import DateFormatter, WeekdayLocator, MonthLocator, DayLocator, MONDAY, AutoDateLocator, AutoDateFormatter
from matplotlib.dates import AutoDateLocator, AutoDateFormatter

import warnings
import pyfolio
from IPython.display import display

# Helper method to merge bar and gap returns into a single period


def getPeriodReturns(returns):
    returns = (returns + 1).prod(axis=1) - 1
    returns.columns = ["period"]
    return returns

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

    #quarters = MonthLocator([1, 3, 6, 9])
    #allmonths = MonthLocator()
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


def getTradingInfo(derivative, startCapital=1):
    ua = derivative.getUnderlyingAllocations() * startCapital
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
        results.append(pd.concat([ua[l1], trade], keys=[
                       "Allocation", "Trade"], axis=1))

    mkts.insert(0, derivative.name)
    results = pd.concat(results, keys=mkts, axis=1)

    # Filter out non-trading periods
    idx = pd.IndexSlice
    return results[
        (results.loc[:, idx[:, :, ['bar', 'gap']]] != 0).any(axis=1)]
