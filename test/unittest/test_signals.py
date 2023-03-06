import unittest
import os
import pandas as pd
import numpy as np
from tradeframework.api.core import Asset
from tradeframework.environments import SandboxEnvironment
from tradeframework.api.insights import InsightManager
import tradeframework.operations.utils as utils
import tradeframework.operations.trader as trader


dir = os.path.dirname(os.path.abspath(__file__))


class SignalsTest(unittest.TestCase):

    def setUp(self):
        marketData = pd.read_csv(dir + "/data/testData3.csv")
        marketData = marketData \
            .reset_index() \
            .assign(Date_Time=lambda x: pd.to_datetime(x['Date_Time'])) \
            .set_index("Date_Time") \
            [["Open", "High", "Low", "Close"]]
        self.marketData = marketData.tz_convert("US/Eastern", level="Date_Time")

    def test_signals(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.createAsset("DOW", self.marketData)

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("TestModel", weightGenerator=env.createModel("TrendFollowing", opts={"start": "15:00", "end": "16:00", "barOnly": True}))
                .addAsset(asset)
            )
        )

        env.refresh()

        #signal = trader.getCurrentSignal(p, capital=10000)

        im = InsightManager(p)
        im.addInsightGenerator(im.createInsightGenerator("Signals", opts={"capital": 10000}))
        signal = im.generateInsights(display=False)["Signals"]

        # Jan'23: Bug: Original value here was based on date that missed July 1st 2013 data!
        # Jan'23: Bug: To ensure test_predictions (below) works, the time series needs to run to 2pm on 2013-07-10
        self.assertTrue(np.allclose(signal["value"], 0.9912554640452014))

    def test_predict(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.createAsset("DOW", self.marketData)

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("TestModel", weightGenerator=env.createModel("TrendFollowing", opts={"start": "15:00", "end": "16:00", "barOnly": True}))
                .addAsset(asset)
            )
        )

        env.refresh()

        possibles = []
        for i in range(-10, 10):
            ohlc = [[15274.38 + i, np.nan, np.nan, np.nan]]
            index = pd.DatetimeIndex(['2013-07-10 15:00:00'], tz='US/Eastern')
            possibles.append(utils.createAssetFromOHLC(index, ohlc, "DOW"))

        #signals = trader.predictSignals(p, possibles)

        im = InsightManager(p)
        im.addInsightGenerator(im.createInsightGenerator("Predictions", opts={"prices": possibles}))
        signals = im.generateInsights(display=False)["Predictions"]

        self.assertEqual(signals[9][0]["markets"][0]["signal"], "SELL")
        self.assertEqual(signals[10][0]["markets"][0]["signal"], "HOLD")
        self.assertEqual(signals[11][0]["markets"][0]["signal"], "BUY")


if __name__ == '__main__':
    unittest.main()
