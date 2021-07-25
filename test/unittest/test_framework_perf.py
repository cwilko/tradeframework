import unittest
import os
import pandas as pd
import numpy as np
import time
import random
import pytest
from tradeframework.api import Asset, Model
from tradeframework.environments import SandboxEnvironment

dir = os.path.dirname(os.path.abspath(__file__))


class FrameworkTestPerf(unittest.TestCase):

    def setUp(self):

        periods = 400
        open = 100
        prices = []
        random.seed(0)
        for i in range(0, periods):
            row = self.generatePrices(open)
            prices.append(row)
            open = row[3]

        self.randomSignals = np.array([random.random() for _ in range(0, periods)])
        self.asset1 = Asset("DOW", pd.DataFrame(prices, columns=["Open", "High", "Low", "Close"], index=pd.date_range(start='1/1/2018', periods=periods)))

    def generatePrices(self, open):
        close = open + (random.random() - .5)
        high = max(open, close) + (random.random() / 2)
        low = min(open, close) - (random.random() / 2)
        return [open, high, low, close]

    def pytest_namespace():
        return {'results': None}

    def test_multiModel_perf(self):

        randomSignals = self.randomSignals

        class RandomModel(Model):

            def getSignals(self, idx=0):
                window = self.assets[0].values[idx:]
                loc = self.assets[0].values.index.get_loc(idx)
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellylWeights", opts={"window": 4}))
        p.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))
        p.addModel(RandomModel("TestModel2", env))

        start = time.time()
        env.append(self.asset1)
        end = time.time()
        print(end - start)

        pytest.results = p.returns["Open"].values.flatten()

        self.assertTrue((end - start) < 1, "Operation took too long")

    def test_multiModel_perf_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = self.randomSignals

        class RandomModel(Model):

            def getSignals(self, idx=0):
                window = self.assets[0].values[idx:]
                loc = self.assets[0].values.index.get_loc(idx)
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellyWeights", opts={"window": 4}))
        p.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))
        p.addModel(RandomModel("TestModel2", env))

        start = time.time()
        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))
        end = time.time()
        print(end - start)
        self.assertTrue((end - start) < 35, "Operation took too long")

        self.assertTrue(np.allclose(
            p.returns["Open"].values.flatten(),
            pytest.results))


if __name__ == '__main__':
    unittest.main()
