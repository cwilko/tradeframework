import unittest
import os
import pandas as pd
import numpy as np
from tradeframework.api import Asset, Model
from tradeframework.environments import SandboxEnvironment
import tradeframework.operations.trader as trader

dir = os.path.dirname(os.path.abspath(__file__))


class FrameworkTest(unittest.TestCase):

    def setUp(self):
        self.asset1 = Asset("DOW", pd.read_csv(dir + '/data/testData1.csv', parse_dates=True, index_col=0, dayfirst=True))

    def test_buyAndHold_singleModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset)
            )
        )

        env.append(self.asset1)
        env.refresh()

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_buyAndHold_singleModel_online(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_buyAndHold_singleModel_online_partials(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset)
            )
        )

        for i in range(len(self.asset1.values)):
            slice = self.asset1.values[i:i + 1].copy()
            slice["Close"] = np.nan
            env.append(Asset("DOW", slice), refreshPortfolio=True)
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_sellAndHold_singleModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-SellAndHold", weightGenerator=env.createModel("SellAndHold"))
                .addAsset(asset)
            )
        )

        env.append(self.asset1)
        env.refresh(self.asset1.values.index[0])

        # Calculate returns manually
        mRet = (0 - np.diff(self.asset1.values["Close"])) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(env.getPortfolio().returns.values[:, 0][1:], mRet.values))

    # Tests using a windowed model
    def test_meanreversion_singleModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-MeanReversion", weightGenerator=env.createModel("MeanReversion"))
                .addAsset(asset)
            )
        )

        env.append(self.asset1)
        env.refresh()

        self.assertTrue(np.allclose(env.getPortfolio().returns["Open"].values.flatten(), [0., 0., 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1]))

    # Tests using a windowed model
    def test_meanreversion_singleModel_online(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-MeanReversion", weightGenerator=env.createModel("MeanReversion"))
                .addAsset(asset)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        self.assertTrue(np.allclose(env.getPortfolio().returns["Open"].values.flatten(), [0., 0., 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1]))

    # Test that partial input (bar only) allocations match full bar/gap input
    def test_meanreversion_singleModel_online_partials(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-MeanReversion", weightGenerator=env.createModel("MeanReversion"))
                .addAsset(asset)
            )
        )

        env.append(Asset("DOW", self.asset1.values[0:-1]), refreshPortfolio=True)

        slice = self.asset1.values[-1:].copy()
        slice["Close"] = np.nan
        env.append(Asset("DOW", slice), refreshPortfolio=True)

        res1 = trader.getUnderlyingAllocations(p)["DOW"]["bar"].values.flatten()

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-MeanReversion", weightGenerator=env.createModel("MeanReversion"))
                .addAsset(asset)
            )
        )

        env.append(Asset("DOW", self.asset1.values), refreshPortfolio=True)

        res2 = trader.getUnderlyingAllocations(p)["DOW"]["bar"].values.flatten()

        self.assertTrue(np.allclose(res1, res2))

    def test_buyAndSell_singleModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, window, idx=0):
                loc = window.index.get_loc(idx)
                signals = pd.DataFrame(np.array([randomSignals[loc:loc + len(window)], randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env))
                .addAsset(asset)
            )
        )

        env.append(self.asset1, refreshPortfolio=True)

        # Calculate returns manually
        mRet = randomSignals[:-1] * np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_buyAndSell_singleModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, window, idx=0):
                loc = window.index.get_loc(idx)
                window = window[idx:]
                signals = pd.DataFrame(np.array([np.zeros(len(window)), randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        # Calculate returns manually
        mRet = randomSignals[:-1] * np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        print(mRet.values)
        print(p.returns.values[:, 0][1:])

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_buyAndSell_multiModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, window, idx=0):
                signals = pd.DataFrame(np.array([np.zeros(len(randomSignals)), randomSignals]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env))
                .addAsset(asset)
            )
        )

        env.append(self.asset1, refreshPortfolio=True)

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], np.array([-.2, .1, -.1, .0, -.1, .0, -.2, .0])))

        # print(trader.getUnderlyingAllocations(p)["DOW"]["gap"].values)

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(trader.getUnderlyingAllocations(p)["DOW"]["gap"].values, np.array([.01, .01, .005, 0, .0051136364, 0, .0104597107, 0, .00475441397])))

    def test_buyAndSell_multiModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, window, idx=0):
                loc = window.index.get_loc(idx)
                window = window[idx:]
                signals = pd.DataFrame(np.array([np.zeros(len(window)), randomSignals[loc:loc + len(window)]]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], np.array([-.2, .1, -.1, .0, -.1, .0, -.2, .0])))

        # print(trader.getUnderlyingAllocations(p)["DOW"]["gap"].values)

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(trader.getUnderlyingAllocations(p)["DOW"]["gap"].values, np.array([.01, .01, .005, 0, .0051136364, 0, .0104597107, 0, .00475441397])))

    def test_kellyWeights_singleModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-1, 1, -1, 1, -1, 1, -1, 1, -1])

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
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer"))
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset)
            )
        )

        env.append(self.asset1, refreshPortfolio=True)

        self.assertTrue(np.allclose(
            p.getAsset("Test-Random").getAllocations()["DOW"]["gap"].values.flatten(),
            [-0.01, 0.015, -0.015, 0.0225, -0.0225, 0.03375, -0.03375, 0.050625, -0.050625]))

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1., 1., 1., 2., 4., 14.90909091, 40.46753247, 202.33766234, 657.5974026]))

    def test_kellyWeights_singleModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-1, 1, -1, 1, -1, 1, -1, 1, -1])

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
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer"))
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        self.assertTrue(np.allclose(
            p.getAsset("Test-Random").getAllocations()["DOW"]["gap"].values.flatten(),
            [-0.01, 0.015, -0.015, 0.0225, -0.0225, 0.03375, -0.03375, 0.050625, -0.050625]))

        print(p.values["Close"].values.flatten())

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1., 1., 1., 2., 4., 14.90909091, 40.46753247, 202.33766234, 657.5974026]))

    def test_kellyWeights_multiModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-.1, .2, -.3, .4, -.5, .6, -.7, .8, -1])

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

        env.append(self.asset1, refreshPortfolio=True)

        self.assertTrue(np.allclose(
            p.returns["Open"].values.flatten(),
            [0., 0., 0., 0., 0., 4.04651163, 6.16666667, 15.26666667, 16.03333333]))

    def test_kellyWeights_multiModel_online(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-.1, .2, -.3, .4, -.5, .6, -.7, .8, -1])

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

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        self.assertTrue(np.allclose(
            p.returns["Open"].values.flatten(),
            [0., 0., 0., 0., 0., 4.04651163, 6.16666667, 15.26666667, 16.03333333]))

    def test_kellyWeights_multiModel_online_partials(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([-.1, .2, -.3, .4, -.5, .6, -.7, .8, -1])

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

        env.append(Asset("DOW", self.asset1.values[0:-1]), refreshPortfolio=True)

        slice = self.asset1.values[-1:].copy()
        slice["Close"] = np.nan
        env.append(Asset("DOW", slice), refreshPortfolio=True)

        res1 = trader.getUnderlyingAllocations(p)["DOW"]["bar"].values.flatten()

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

        env.append(Asset("DOW", self.asset1.values), refreshPortfolio=True)

        res2 = trader.getUnderlyingAllocations(p)["DOW"]["bar"].values.flatten()

        self.assertTrue(np.allclose(res1, res2))

    # Tests using a windowed model
    def test_combi_singleModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio")
            .addAsset(
                env.createDerivative("Indicators")
                .addAsset(
                    env.createDerivative("MeanReversionIndicator", weightGenerator=env.createModel("MeanReversion"))
                    .addAsset(asset)
                )
                .addAsset(
                    env.createDerivative("BuyAndHoldIndicator", weightGenerator=env.createModel("BuyAndHold"))
                    .addAsset(asset)
                ),
                weighted=False
            )
            .addAsset(
                env.createDerivative("CombiMRAndBuy", weightGenerator=env.createModel("CombinationModel", opts={"modelList": ["MeanReversionIndicator", "BuyAndHoldIndicator"]}))
                .addAsset(asset)
            )
        )

        env.append(self.asset1, refreshPortfolio=True)

        self.assertTrue(np.allclose(p.returns["Open"].values.flatten(), [0., 0., 0.1, 0., 0.1, 0., 0.1, 0., 0.1]))

    # Tests using a windowed model
    def test_combi_singleModel_online(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Indicators")
                .addAsset(
                    env.createDerivative("MeanReversionIndicator", weightGenerator=env.createModel("MeanReversion"))
                    .addAsset(asset)
                )
                .addAsset(
                    env.createDerivative("BuyAndHoldIndicator", weightGenerator=env.createModel("BuyAndHold"))
                    .addAsset(asset)
                ),
                weighted=False
            )
            .addAsset(
                env.createDerivative("CombiMRAndBuy", weightGenerator=env.createModel("CombinationModel", opts={"modelList": ["MeanReversionIndicator", "BuyAndHoldIndicator"]}))
                .addAsset(asset)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        self.assertTrue(np.allclose(p.returns["Open"].values.flatten(), [0., 0., 0.1, 0., 0.1, 0., 0.1, 0., 0.1]))

    # Test that partial input (bar only) allocations match full bar/gap input
    def test_combi_singleModel_online_partials(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Indicators")
                .addAsset(
                    env.createDerivative("MeanReversionIndicator", weightGenerator=env.createModel("MeanReversion"))
                    .addAsset(asset)
                )
                .addAsset(
                    env.createDerivative("BuyAndHoldIndicator", weightGenerator=env.createModel("BuyAndHold"))
                    .addAsset(asset)
                ),
                weighted=False
            )
            .addAsset(
                env.createDerivative("CombiMRAndBuy", weightGenerator=env.createModel("CombinationModel", opts={"modelList": ["MeanReversionIndicator", "BuyAndHoldIndicator"]}))
                .addAsset(asset)
            )
        )

        env.append(Asset("DOW", self.asset1.values[0:-1]), refreshPortfolio=True)

        slice = self.asset1.values[-1:].copy()
        slice["Close"] = np.nan
        env.append(Asset("DOW", slice), refreshPortfolio=True)

        res1 = trader.getUnderlyingAllocations(p)["DOW"]["bar"].values.flatten()

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Indicators", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
                .addAsset(
                    env.createDerivative("MeanReversionIndicator", weightGenerator=env.createModel("MeanReversion"))
                    .addAsset(asset)
                )
                .addAsset(
                    env.createDerivative("BuyAndHoldIndicator", weightGenerator=env.createModel("BuyAndHold"))
                    .addAsset(asset)
                ),
                weighted=False
            )
            .addAsset(
                env.createDerivative("CombiMRAndBuy", weightGenerator=env.createModel("CombinationModel", opts={"modelList": ["MeanReversionIndicator", "BuyAndHoldIndicator"]}))
                .addAsset(asset)
            )
        )

        env.append(Asset("DOW", self.asset1.values), refreshPortfolio=True)

        res2 = trader.getUnderlyingAllocations(p)["DOW"]["bar"].values.flatten()

        self.assertTrue(np.allclose(res1, res2))

if __name__ == '__main__':
    unittest.main()
