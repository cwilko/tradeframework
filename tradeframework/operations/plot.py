import numpy as np
import pandas as pd

import quantutils.core.statistics as stats
from quantutils.core.plot import OHLCChart
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, AutoDateFormatter
import tradeframework.operations.utils as utils

import warnings
import pyfolio
from IPython.display import display

# Plot Candlestick chart for an asset


def plotAsset(asset, options=None):
    chart = OHLCChart(options)
    chart.addSeries(asset.getName(), asset.values.reset_index().values.tolist())
    display(chart.getChart())
    return chart


def plotUnderlying(derivative, underlyingName, options=None):
    return plotAsset(derivative.env.getAssetStore().getAsset(underlyingName))


def plotWeightedUnderlying(derivative, underlyingName, options=None):
    underlying = derivative.env.getAssetStore().getAsset(underlyingName)
    asset = underlying.values.mul(derivative.weights[underlyingName]["bar"].values, axis=0)
    asset.replace(0, np.nan, inplace=True)
    chart = OHLCChart(options)
    chart.addSeries(underlyingName, asset.reset_index().values.tolist())
    display(chart.getChart())
    return chart

# Helper method to pretty print derviative performance


def plotReturns(derivative, baseline=None, log=False, includeComponents=False, includePrimary=True, custom=[]):

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
        pnl = lambda x: np.cumsum(np.log((utils.getPeriodReturns(x.returns[np.prod(derivative.values, axis=1) != 1]) + 1).resample('B').agg('prod')))
    else:
        pnl = lambda x: np.cumprod((utils.getPeriodReturns(x.returns[np.prod(derivative.values, axis=1) != 1]) + 1).resample('B').agg('prod'))

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
