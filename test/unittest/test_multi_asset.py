import unittest
import os
import pandas as pd
import numpy as np
from tradeframework.api.core import Asset, Model
from tradeframework.environments import SandboxEnvironment
import tradeframework.operations.trader as trader

dir = os.path.dirname(os.path.abspath(__file__))


class MultiAssetTest(unittest.TestCase):

    def setUp(self):
        self.asset1 = Asset("DOW", pd.read_csv(dir + '/data/testData1.csv', parse_dates=True, index_col=0, dayfirst=True))
        self.asset2 = Asset("SPY", pd.read_csv(dir + '/data/testData2.csv', parse_dates=True, index_col=0, dayfirst=True))

    def test_buyAndHold_singleModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        env.append(self.asset1)
        env.append(self.asset2)
        env.refresh()

        # Calculate returns manually
        mRet1 = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]
        mRet2 = np.diff(self.asset2.values["Close"]) / self.asset2.values["Close"][:-1]
        mRet = np.sum([mRet1, mRet2], axis=0)

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet))

    def test_buyAndHold_singleModel_online(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )
        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=False)
            env.append(Asset("SPY", self.asset2.values[i:i + 1]), refreshPortfolio=False)
            env.refresh(self.asset1.values[i:i + 1].index[0])

        # Calculate returns manually
        mRet1 = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]
        mRet2 = np.diff(self.asset2.values["Close"]) / self.asset2.values["Close"][:-1]
        mRet = np.sum([mRet1, mRet2], axis=0)

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet))

    def test_buyAndHold_singleModel_online_partials(self):

               # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        for i in range(len(self.asset1.values)):
            slice1 = self.asset1.values[i:i + 1].copy()
            slice1["Close"] = np.nan
            env.append(Asset("DOW", slice1), refreshPortfolio=False)

            slice2 = self.asset2.values[i:i + 1].copy()
            slice2["Close"] = np.nan
            env.append(Asset("SPY", slice2), refreshPortfolio=False)
            env.refresh(slice1.index[0])

            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=False)
            env.append(Asset("SPY", self.asset2.values[i:i + 1]), refreshPortfolio=False)
            env.refresh(slice1.index[0])

        # Calculate returns manually
        mRet1 = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]
        mRet2 = np.diff(self.asset2.values["Close"]) / self.asset2.values["Close"][:-1]
        mRet = np.sum([mRet1, mRet2], axis=0)

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet))

    def test_sellAndHold_singleModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-SellAndHold", weightGenerator=env.createModel("SellAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        env.append(self.asset1)
        env.append(self.asset2)
        env.refresh()

        # Calculate returns manually
        mRet1 = (0 - np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1])
        mRet2 = (0 - np.diff(self.asset2.values["Close"]) / self.asset2.values["Close"][:-1])
        mRet = np.sum([mRet1, mRet2], axis=0)

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet))

    # Tests using a windowed model
    def test_meanreversion_singleModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-MeanReversion", weightGenerator=env.createModel("MeanReversion"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        env.append(self.asset1)
        env.append(self.asset2)
        env.refresh()

        self.assertTrue(np.allclose(env.getPortfolio().returns["Open"].values.flatten(), [0., 0., 0.2, 0.4, 0.2, 0.4, 0.2, 0.4, 0.2]))

    # Tests using a windowed model
    def test_meanreversion_singleModel_online(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-MeanReversion", weightGenerator=env.createModel("MeanReversion"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=False)
            env.append(Asset("SPY", self.asset2.values[i:i + 1]), refreshPortfolio=False)
            env.refresh(self.asset1.values[i:i + 1].index[0])

        self.assertTrue(np.allclose(env.getPortfolio().returns["Open"].values.flatten(), [0., 0., 0.2, 0.4, 0.2, 0.4, 0.2, 0.4, 0.2]))

    def test_buyAndSell_multiModel(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, window, idx=0):
                signals = pd.DataFrame(np.array([np.zeros(len(randomSignals)), randomSignals]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        env.append(self.asset1, refreshPortfolio=False)
        env.append(self.asset2, refreshPortfolio=False)
        env.refresh()

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], np.array([.0, .0, .0, .0, .0, .0, .0, .0])))

        # print(trader.getUnderlyingAllocations(p)["DOW"]["gap"].values)

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(trader.getUnderlyingAllocations(p)["DOW"]["gap"].values, np.array([1.00000000e-02, 1.25000000e-02, 5.68181818e-03, 0.00000000e+00,
                                                                                                       6.45661157e-03, 1.73472348e-18, 1.46741172e-02, 0.00000000e+00,
                                                                                                       8.33756659e-03])))

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
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=False)
            env.append(Asset("SPY", self.asset2.values[i:i + 1]), refreshPortfolio=False)
            env.refresh(self.asset1.values[i:i + 1].index[0])

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], np.array([.0, .0, .0, .0, .0, .0, .0, .0])))

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(trader.getUnderlyingAllocations(p)["SPY"]["gap"].values, np.array([1.00000000e-02, 8.33333333e-03, 4.62962963e-03, 0.00000000e+00,
                                                                                                       4.28669410e-03, 4.33680869e-19, 7.93832241e-03, 4.33680869e-19,
                                                                                                       3.67514926e-03])))

    def test_kellyWeights_singleModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        env.append(self.asset1, refreshPortfolio=False)
        env.append(self.asset2, refreshPortfolio=False)
        env.refresh()

        self.assertTrue(np.allclose(
            p.getAsset("Test-BuyAndHold").getAllocations()["DOW"]["gap"].values.flatten(),
            [0.01, 0.0125, 0.01136364, 0.01420455, 0.01291322, 0.01614153, 0.01467412, 0.01834265, 0.01667513]))

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1., 1., 1., 1., 1., 1., 1., 1., 1.]))

    def test_kellyWeights_singleModel_online(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=False)
            env.append(Asset("SPY", self.asset2.values[i:i + 1]), refreshPortfolio=False)
            env.refresh(self.asset1.values[i:i + 1].index[0])

        self.assertTrue(np.allclose(
            p.getAsset("Test-BuyAndHold").getAllocations()["DOW"]["gap"].values.flatten(),
            [0.01, 0.0125, 0.01136364, 0.01420455, 0.01291322, 0.01614153, 0.01467412, 0.01834265, 0.01667513]))

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1., 1., 1., 1., 1., 1., 1., 1., 1.]))

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
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer", opts={"window": 4}))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        env.append(self.asset1, refreshPortfolio=False)
        env.append(self.asset2, refreshPortfolio=False)
        env.refresh(self.asset1.values.index[0])

        self.assertTrue(np.allclose(
            p.returns["Open"].values.flatten(),
            [0., 0., 0., 0., 0., 0., 0., 0., 0.]))

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
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer", opts={"window": 4}))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=False)
            env.append(Asset("SPY", self.asset2.values[i:i + 1]), refreshPortfolio=False)
            env.refresh(self.asset1.values[i:i + 1].index[0])

        self.assertTrue(np.allclose(
            p.returns["Open"].values.flatten(),
            [0., 0., 0., 0., 0., 0., 0., 0., 0.]))

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
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer", opts={"window": 4}))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        env.append(Asset("DOW", self.asset1.values[0:-1]), refreshPortfolio=False)
        env.append(Asset("SPY", self.asset2.values[0:-1]), refreshPortfolio=False)
        env.refresh(self.asset1.values.index[0])

        slice1 = self.asset1.values[-1:].copy()
        slice1["Close"] = np.nan
        env.append(Asset("DOW", slice1), refreshPortfolio=False)

        slice2 = self.asset2.values[-1:].copy()
        slice2["Close"] = np.nan
        env.append(Asset("SPY", slice2), refreshPortfolio=False)

        env.refresh(slice1.index[0])

        res1 = trader.getUnderlyingAllocations(p)["DOW"]["bar"].values.flatten()

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer", opts={"window": 4}))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
                .addAsset(asset2)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset1)
                .addAsset(asset2)
            )
        )

        env.append(Asset("DOW", self.asset1.values), refreshPortfolio=False)
        env.append(Asset("SPY", self.asset2.values), refreshPortfolio=False)
        env.refresh(self.asset1.values.index[0])

        res2 = trader.getUnderlyingAllocations(p)["DOW"]["bar"].values.flatten()

        self.assertTrue(np.allclose(res1, res2))

    def test_multiModel_mixedAsset(self):

        # randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
        randomSignals = np.array([1, 1, 0, -1, 0, -1, 1, -1, 0])

        class RandomModel(Model):

            def getSignals(self, window, idx=0):
                signals = pd.DataFrame(np.array([np.zeros(len(randomSignals)), randomSignals]).T, index=window.index, columns=["bar", "gap"])
                return signals

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset1 = env.append(Asset("DOW"))
        asset2 = env.append(Asset("SPY"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset1)
            )
            .addAsset(
                env.createDerivative("Test-Random", weightGenerator=RandomModel(env, window=-1))
                .addAsset(asset2)
            )
        )

        env.append(self.asset1, refreshPortfolio=False)
        env.append(self.asset2, refreshPortfolio=False)
        env.refresh()

        # Test returns were calculated correctly
        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], np.array([0.00000000e+00, 0.00000000e+00, -1.00000000e-01, 1.00000000e-01,
                                                                          -1.00000000e-01, 1.00000000e-01, -1.13276505e-16, 1.00000000e-01])))

        # print(trader.getUnderlyingAllocations(p)["DOW"]["gap"].values)

        # Test underlying allocations were calculated correctly
        self.assertTrue(np.allclose(trader.getUnderlyingAllocations(p)["DOW"]["gap"].values, np.array([0.005, 0.00625, 0.00568182, 0.00639205, 0.00639205,
                                                                                                       0.00719105, 0.00719105, 0.00898881, 0.00898881])))

if __name__ == '__main__':
    unittest.main()
