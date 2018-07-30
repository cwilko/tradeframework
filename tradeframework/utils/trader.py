import numpy as np
import pandas as pd 

import quantutils.core.statistics as stats
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY

import warnings
import pyfolio
from IPython.display import display

# Helper method to merge bar and gap returns into a single period
def getPeriodReturns(returns):
    returns = (returns + 1).prod(axis=1)-1
    returns.columns = ["period"]
    return returns

# Helper method to pretty print derviative performance
def plot(dInfo, baseline=None, log=False, includeComponents=False, includePrimary=True):
    
    assets = []
    
    # Add component asset returns
    if (includeComponents):
        assets = dInfo.assets[:]
        
    # Add primary returns
    if (includePrimary):
        assets.append(dInfo)
    
    # Add baseline
    if (baseline is not None):
        assets.append(baseline)
        
    if (log):
        pnl = lambda x : np.cumsum(np.log((getPeriodReturns(x.returns) + 1).resample('B').agg('prod')))
    else:
        pnl = lambda x : np.cumprod((getPeriodReturns(x.returns) + 1).resample('B').agg('prod'))

    mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    alldays = DayLocator()              # minor ticks on the days
    weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    
    for asset in assets:
        ax.plot(pnl(asset), label=asset.name)
            
    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.title("Derivative performance")
    plt.legend(loc='best')
    plt.show() 

def displaySummary(dInfo, tInfo, baseline=None, log=False, includeComponents=True, includePrimary=True):
    print("Derivative name : " + dInfo.name)
    print("Number of assets : " + str(len(dInfo.assets)))
    if (baseline is not None):
        print("Baseline name : " + baseline.name)
    
    # Summary plot
    plot(dInfo, baseline, log, includeComponents, includePrimary)
            
    # Show sample of trades
    pd.set_option('display.max_rows', 10)    
    display(tInfo)
    
    # Show local statistics
    stats.merton(dInfo.returns["Open"][dInfo.returns["Open"]!=0], baseline.returns["Open"][baseline.returns["Open"]!=0], display=True) 
    
    # Show generic statistics
    warnings.filterwarnings('ignore')
    pyfolio.create_returns_tear_sheet(getPeriodReturns(dInfo.returns))    