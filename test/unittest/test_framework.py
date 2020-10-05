import unittest
import os
import pandas as pd
import numpy as np
from tradeframework.api import Asset, Model, append_asset
from tradeframework.environments import SandboxEnvironment

dir = os.path.dirname(os.path.abspath(__file__))


class FrameworkTest(unittest.TestCase):

    def setUp(self):
        self.asset1 = Asset("DOW", pd.read_csv(dir + '/data/testData1.csv', parse_dates=True, index_col=0, dayfirst=True))

    def test_buyAndHold_singleModel(self):

        class BuyAndHoldModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.ones((len(asset.values), 2)), index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(BuyAndHoldModel("TestModel", env))
        dInfo = env.handleData(self.asset1)

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(dInfo.returns.values[:, 1][:-1], mRet.values))

    def test_SellAndHold_singleModel(self):

        class SellAndHoldModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(0 - np.ones((len(asset.values), 2)), index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(SellAndHoldModel("TestModel", env))
        dInfo = env.handleData(self.asset1)

        # Calculate returns manually
        mRet = (0 - np.diff(self.asset1.values["Close"])) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(dInfo.returns.values[:, 1][:-1], mRet.values))

    def test_buyAndSell_singleModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([np.zeros(len(randomSignals)), randomSignals]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(RandomModel("SellAndHold", env))
        dInfo = env.handleData(self.asset1)

        # Calculate returns manually
        mRet = randomSignals[:-1] * np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(dInfo.returns.values[:, 1][:-1], mRet.values))

    def test_buyAndSell_singleModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([np.zeros(len(asset.values)), randomSignals[:len(asset.values)]]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(RandomModel("SellAndHold", env))

        for i in range(len(self.asset1.values)):
            env.handleData(Asset("DOW", self.asset1.values[i:i + 1]))

        # Calculate returns manually
        mRet = randomSignals[:-1] * np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 1][:-1], mRet.values))

    def test_buyAndSell_multiModel(self):

        class BuyAndHoldModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([np.zeros(len(asset.values)), np.ones(len(asset.values))]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([np.zeros(len(randomSignals)), randomSignals]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(BuyAndHoldModel("TestModel", env))
        p.addModel(RandomModel("TestModel2", env))
        dInfo = env.handleData(self.asset1)

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(dInfo.returns.values[:, 1][:-1], np.array([-.2, .1, -.1, .0, -.1, .0, -.2, .0])))

        print(dInfo.getUnderlyingAllocations()["DOW"]["gap"].values)

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(dInfo.getUnderlyingAllocations()["DOW"]["gap"].values, np.array([.01, .01, .005, 0, .0051136364, 0, .0104597107, 0, .00475441397])))

    def test_buyAndSell_multiModel_online(self):

        class BuyAndHoldModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([np.zeros(len(asset.values)), np.ones(len(asset.values))]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([np.zeros(len(asset.values)), randomSignals[:len(asset.values)]]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
        p.addModel(BuyAndHoldModel("TestModel", env))
        p.addModel(RandomModel("TestModel2", env))

        for i in range(len(self.asset1.values)):
            env.handleData(Asset("DOW", self.asset1.values[i:i + 1]))

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(p.returns.values[:, 1][:-1], np.array([-.2, .1, -.1, .0, -.1, .0, -.2, .0])))

        print(p.getUnderlyingAllocations()["DOW"]["gap"].values)

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(p.getUnderlyingAllocations()["DOW"]["gap"].values, np.array([.01, .01, .005, 0, .0051136364, 0, .0104597107, 0, .00475441397])))

    def test_kellyWeights_singleModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-1, 1, -1, 1, -1, 1, -1, 1, -1])

        class RandomModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([randomSignals, randomSignals]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellylWeights"))
        p.addModel(RandomModel("TestModel", env))
        env.handleData(self.asset1)

        self.assertTrue(np.allclose(
            p.getAsset("TestModel").getAllocations()["DOW"]["gap"].values.flatten(),
            [-0.01, 0.015, -0.015, 0.0225, -0.0225, 0.03375, -0.03375, 0.050625, -0.050625]))

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1.0000e+00, 1.0000e+00, 1.0000e+00, 7.0000e+00, 4.2000e+01, 4.2000e+02, 2.6600e+03, 2.9260e+04, 1.9019e+05]))

    def test_kellyWeights_singleModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-1, 1, -1, 1, -1, 1, -1, 1, -1])

        class RandomModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([np.zeros(len(asset.values)), randomSignals[:len(asset.values)]]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellylWeights"))
        p.addModel(RandomModel("TestModel", env))

        for i in range(len(self.asset1.values)):
            env.handleData(Asset("DOW", self.asset1.values[i:i + 1]))

        self.assertTrue(np.allclose(
            p.getAsset("TestModel").getAllocations()["DOW"]["gap"].values.flatten(),
            [-0.01, 0.015, -0.015, 0.0225, -0.0225, 0.03375, -0.03375, 0.050625, -0.050625]))

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1.0000e+00, 1.0000e+00, 1.0000e+00, 7.0000e+00, 4.2000e+01, 4.2000e+02, 2.6600e+03, 2.9260e+04, 1.9019e+05]))

    def test_kellyWeights_multiModel(self):

        class BuyAndHoldModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.ones((len(asset.values), 2)), index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-1, 1, -1, 1, -1, 1, -1, 1, -1])

        class RandomModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([randomSignals, randomSignals]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellylWeights", opts={"window": 4}))
        p.addModel(BuyAndHoldModel("TestModel", env))
        p.addModel(RandomModel("TestModel2", env))
        env.handleData(self.asset1)

        self.assertTrue(np.allclose(
            p.returns["Close"].values.flatten(),
            [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 4.0992764608e+16, 2.0496382304e+16, 4.0992764608e+16, 0.0000000000e+00]))

    def test_kellyWeights_multiModel_online(self):

        class BuyAndHoldModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.ones((len(asset.values), 2)), index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-1, 1, -1, 1, -1, 1, -1, 1, -1])

        class RandomModel(Model):

            @append_asset
            def handleData(self, asset):
                signals = pd.DataFrame(np.array([np.zeros(len(asset.values)), randomSignals[:len(asset.values)]]).T, index=asset.values.index, columns=["bar", "gap"])
                return self.update([asset], [signals])

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellyWeights", opts={"window": 4}))
        p.addModel(BuyAndHoldModel("TestModel", env))
        p.addModel(RandomModel("TestModel2", env))

        for i in range(len(self.asset1.values)):
            env.handleData(Asset("DOW", self.asset1.values[i:i + 1]))

        self.assertTrue(np.allclose(
            p.returns["Close"].values.flatten(),
            [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 4.0992764608e+16, 2.0496382304e+16, 4.0992764608e+16, 0.0000000000e+00]))


if __name__ == '__main__':
    unittest.main()
