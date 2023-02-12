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

            def getSignals(self, window, idx=0):
                loc = window.index.get_loc(idx)
                window = window[idx:]
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer", opts={"window": 4}))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset)
            )
        )

        start = time.time()
        env.append(self.asset1, refreshPortfolio=True)
        end = time.time()
        print(end - start)

        pytest.results = p.returns["Open"].values.flatten()

        self.assertTrue((end - start) < 1, "Operation took too long")

    def test_multiModel_perf_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = self.randomSignals

        class RandomModel(Model):

            def getSignals(self, window, idx=0):
                loc = window.index.get_loc(idx)
                window = window[idx:]
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer", opts={"window": 4}))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset)
            )
        )

        start = time.time()
        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)
        end = time.time()
        print(end - start)
        self.assertTrue((end - start) < 35, "Operation took too long")

        self.assertTrue(np.allclose(
            p.returns["Open"].values.flatten(),
            pytest.results))


if __name__ == '__main__':
    unittest.main()
