import unittest
import os
import pandas as pd
import numpy as np
from tradeframework.api import Asset, Model
from tradeframework.environments import SandboxEnvironment
import tradeframework.operations.trader as trader

dir = os.path.dirname(os.path.abspath(__file__))


class TopologyTest(unittest.TestCase):

    def setUp(self):
        self.asset1 = Asset("DOW", pd.read_csv(dir + '/data/testData1.csv', parse_dates=True, index_col=0, dayfirst=True))

    def test_noModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.createAsset("DOW")

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(asset)
        )

        env.append(self.asset1)
        env.refresh()

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_noModel_online(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.createAsset("DOW")

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(asset)
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_mix_model_noModel(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.createAsset("DOW")

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(asset)
            )
            .addAsset(asset)
        )

        env.append(self.asset1)
        env.refresh()

        # Calculate returns manually
        mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

        self.assertTrue(np.allclose(p.returns.values[:, 0][1:], mRet.values))

    def test_nested_portfolios(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(
                    env.createDerivative("NestedPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer"))
                    .addAsset(
                        env.createDerivative("Test-BuyAndHold2", weightGenerator=env.createModel("BuyAndHold"))
                        .addAsset(asset)
                    )
                )
            )
        )

        env.append(self.asset1)
        env.refresh()

        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1., 1., 1., 2., 1.71428571, 2.85714286, 2.36024845, 3.74862989, 3.04576178]))

    def test_nested_portfolios_online(self):

        # Create portfolio
        env = SandboxEnvironment("TradeFair")
        asset = env.append(Asset("DOW"))

        p = env.setPortfolio(
            env.createDerivative("MyPortfolio", weightGenerator=env.createOptimizer("EqualWeightsOptimizer"))
            .addAsset(
                env.createDerivative("Test-BuyAndHold", weightGenerator=env.createModel("BuyAndHold"))
                .addAsset(
                    env.createDerivative("NestedPortfolio", weightGenerator=env.createOptimizer("KellyOptimizer"))
                    .addAsset(
                        env.createDerivative("Test-BuyAndHold2", weightGenerator=env.createModel("BuyAndHold"))
                        .addAsset(asset)
                    )
                )
            )
        )

        for i in range(len(self.asset1.values)):
            env.append(Asset("DOW", self.asset1.values[i:i + 1]), refreshPortfolio=True)

        # Calculate returns manually
        self.assertTrue(np.allclose(
            p.values["Close"].values.flatten(),
            [1., 1., 1., 2., 1.71428571, 2.85714286, 2.36024845, 3.74862989, 3.04576178]))

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
