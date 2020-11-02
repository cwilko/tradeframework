import unittest
import os
import pandas as pd
import numpy as np
from tradeframework.api import Asset, Model
from tradeframework.environments import SandboxEnvironment

dir = os.path.dirname(os.path.abspath(__file__))

# TODO : Add Test using a Windowed model


class FrameworkTest(unittest.TestCase):

    def setUp(self):
        self.asset1 = Asset("DOW", pd.read_csv(dir + '/data/testData1.csv', parse_dates=True, index_col=0, dayfirst=True))

    def test_buyAndHold_singleModel(self):

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))
        dInfo = env.append(self.asset1)

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(dInfo.returns.values[:, 0][1:], mRet.values))

    def test_buyAndHold_singleModel_online(self):

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_buyAndHold_singleModel_online_partials(self):

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))

        for i in range(len(self.asset1.values)):
            slice = self.asset1.values[i:i + 1].copy()
            slice["Close"] = np.nan
            env.append(Asset("DOW", slice))
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_sellAndHold_singleModel(self):

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("SellAndHold", "Test-SellAndHold"))
        dInfo = env.append(self.asset1)

        # Calculate returns manually
        mRet = (0 - np.diff(self.asset1.values["Close"])) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(dInfo.returns.values[:, 0][1:], mRet.values))

    # Tests using a windowed model
    def test_meanreversion_singleModel(self):

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("MeanReversion", "Test-MeanReversion"))
        dInfo = env.append(self.asset1)

        self.assertTrue(np.allclose(dInfo.returns["Open"].values.flatten(), [0., 0., 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1]))

    # Tests using a windowed model
    def test_meanreversion_singleModel_online(self):

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("MeanReversion", "Test-MeanReversion"))
        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))

        self.assertTrue(np.allclose(p.returns["Open"].values.flatten(), [0., 0., 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1]))

    # Test that partial input (bar only) allocations match full bar/gap input
    def test_meanreversion_singleModel_online_partials(self):

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("MeanReversion", "Test-BuyAndHold"))

        env.append(Asset("DOW", self.asset1.values[0:-1]))

        slice = self.asset1.values[-1:].copy()
        slice["Close"] = np.nan
        env.append(Asset("DOW", slice))

        res1 = p.getUnderlyingAllocations()["DOW"]["bar"].values.flatten()

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("MeanReversion", "Test-BuyAndHold"))

        env.append(Asset("DOW", self.asset1.values))

        res2 = p.getUnderlyingAllocations()["DOW"]["bar"].values.flatten()

        self.assertTrue(np.allclose(res1, res2))

    def test_buyAndSell_singleModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, idx=0):
                window = self.assets[0].values[idx:]
                loc = self.assets[0].values.index.get_loc(idx)
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(RandomModel("RandomModel", env))
        dInfo = env.append(self.asset1)

        # Calculate returns manually
        mRet = randomSignals[:-1] * np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(dInfo.returns.values[:, 0][1:], mRet.values))

    def test_buyAndSell_singleModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, idx=0):
                window = self.assets[0].values[idx:]
                loc = self.assets[0].values.index.get_loc(idx)
                signals = pd.DataFrame(np.array([np.zeros(len(window)), randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(RandomModel("RandomModel", env))

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))

        # Calculate returns manually
        mRet = randomSignals[:-1] * np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_buyAndSell_multiModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, idx=0):
                signals = pd.DataFrame(np.array([np.zeros(len(randomSignals)), randomSignals]).T, index=self.assets[0].values.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))
        p.addModel(RandomModel("TestModel2", env))
        dInfo = env.append(self.asset1)

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(dInfo.returns.values[:, 0][1:], np.array([-.2, .1, -.1, .0, -.1, .0, -.2, .0])))

        print(dInfo.getUnderlyingAllocations()["DOW"]["gap"].values)

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(dInfo.getUnderlyingAllocations()["DOW"]["gap"].values, np.array([.01, .01, .005, 0, .0051136364, 0, .0104597107, 0, .00475441397])))

    def test_buyAndSell_multiModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, idx=0):
                window = self.assets[0].values[idx:]
                loc = self.assets[0].values.index.get_loc(idx)
                signals = pd.DataFrame(np.array([np.zeros(len(window)), randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))
        p.addModel(RandomModel("TestModel2", env))

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], np.array([-.2, .1, -.1, .0, -.1, .0, -.2, .0])))

        print(p.getUnderlyingAllocations()["DOW"]["gap"].values)

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(p.getUnderlyingAllocations()["DOW"]["gap"].values, np.array([.01, .01, .005, 0, .0051136364, 0, .0104597107, 0, .00475441397])))

    def test_kellyWeights_singleModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-1, 1, -1, 1, -1, 1, -1, 1, -1])

        class RandomModel(Model):

            def getSignals(self, idx=0):
                window = self.assets[0].values[idx:]
                loc = self.assets[0].values.index.get_loc(idx)
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellylWeights"))
        p.addModel(RandomModel("TestModel", env))
        env.append(self.asset1)

        self.assertTrue(np.allclose(
            p.getAsset("TestModel").getAllocations()["DOW"]["gap"].values.flatten(),
            [-0.01, 0.015, -0.015, 0.0225, -0.0225, 0.03375, -0.03375, 0.050625, -0.050625]))

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1., 1., 1., 2., 4., 14.90909091, 40.46753247, 202.33766234, 657.5974026]))

    def test_kellyWeights_singleModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-1, 1, -1, 1, -1, 1, -1, 1, -1])

        class RandomModel(Model):

            def getSignals(self, idx=0):
                window = self.assets[0].values[idx:]
                loc = self.assets[0].values.index.get_loc(idx)
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellylWeights"))
        p.addModel(RandomModel("TestModel", env))

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))

        self.assertTrue(np.allclose(
            p.getAsset("TestModel").getAllocations()["DOW"]["gap"].values.flatten(),
            [-0.01, 0.015, -0.015, 0.0225, -0.0225, 0.03375, -0.03375, 0.050625, -0.050625]))

        print(p.values["Close"].values.flatten())

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1., 1., 1., 2., 4., 14.90909091, 40.46753247, 202.33766234, 657.5974026]))

    def test_kellyWeights_multiModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-.1, .2, -.3, .4, -.5, .6, -.7, .8, -1])

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
        env.append(self.asset1)

        self.assertTrue(np.allclose(
            p.returns["Open"].values.flatten(),
            [0., 0., 0., 0., 0., 4.04651163, 6.16666667, 15.26666667, 16.03333333]))

    def test_kellyWeights_multiModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-.1, .2, -.3, .4, -.5, .6, -.7, .8, -1])

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

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))

        self.assertTrue(np.allclose(
            p.returns["Open"].values.flatten(),
            [0., 0., 0., 0., 0., 4.04651163, 6.16666667, 15.26666667, 16.03333333]))

    def test_kellyWeights_multiModel_online_partials(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-.1, .2, -.3, .4, -.5, .6, -.7, .8, -1])

        class RandomModel(Model):

            def getSignals(self, idx=0):
                window = self.assets[0].values[idx:]
                loc = self.assets[0].values.index.get_loc(idx)
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Calculate returns via TradeFramework for a partial input (bar only)
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellyWeights", opts={"window": 4}))
        p.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))
        p.addModel(RandomModel("TestModel2", env))

        env.append(Asset("DOW", self.asset1.values[0:-1]))

        slice = self.asset1.values[-1:].copy()
        slice["Close"] = np.nan
        env.append(Asset("DOW", slice))

        res1 = p.getUnderlyingAllocations()["DOW"]["bar"].values.flatten()

        # Calculate returns via TradeFramework for a full input (bar/gap)
        env = SandboxEnvironment("TradeFair")
        p2 = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellyWeights", opts={"window": 4}))
        p2.addModel(env.createModel("BuyAndHold", "Test-BuyAndHold"))
        p2.addModel(RandomModel("TestModel2", env))

        env.append(Asset("DOW", self.asset1.values))

        res2 = p2.getUnderlyingAllocations()["DOW"]["bar"].values.flatten()

        self.assertTrue(np.allclose(res1, res2))
