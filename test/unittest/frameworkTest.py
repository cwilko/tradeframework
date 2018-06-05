import unittest
import pandas as pd
import numpy as np
from tradeframework.api import AssetInfo, Model
from tradeframework.environments import SandboxEnvironment

class FrameworkTest(unittest.TestCase):

	def setUp(self):
		self.asset1 = AssetInfo("DOW", pd.read_csv('data/testData1.csv', parse_dates=True, index_col=0, dayfirst=True))

	def test_buyAndHold_singleModel(self):

		class BuyAndHoldModel(Model):
			def handleData(self, context, assetInfo):
				signals = pd.DataFrame(np.ones((len(assetInfo.values), 2)), index=assetInfo.values.index, columns=["bar","gap"])
				return self.getDerivativeInfo(context, [assetInfo], [signals])

		# Calculate returns via TradeFramework
		env = SandboxEnvironment("TradeFair")
		p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
		p.addModel(BuyAndHoldModel("TestModel", env))
		dInfo = env.handleData({}, self.asset1)

		# Calculate returns manually
		mRet = np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

		self.assertTrue(np.allclose(dInfo.returns.values[:,1][:-1],mRet.values))

	def test_SellAndHold_singleModel(self):

		class SellAndHoldModel(Model):
			def handleData(self, context, assetInfo):
				signals = pd.DataFrame(0 - np.ones((len(assetInfo.values), 2)), index=assetInfo.values.index, columns=["bar","gap"])
				return self.getDerivativeInfo(context, [assetInfo], [signals])

		# Calculate returns via TradeFramework
		env = SandboxEnvironment("TradeFair")
		p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
		p.addModel(SellAndHoldModel("TestModel", env))
		dInfo = env.handleData({}, self.asset1)

		# Calculate returns manually
		mRet = (0 - np.diff(self.asset1.values["Close"])) / self.asset1.values["Close"][:-1]

		self.assertTrue(np.allclose(dInfo.returns.values[:,1][:-1],mRet.values))

	def test_buyAndSell_singleModel(self):

		# randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
		randomSignals = np.array([1,1,0,-1,0,-1,1,-1,0])

		class RandomModel(Model):
			def handleData(self, context, assetInfo):
				signals = pd.DataFrame(np.array([np.zeros(len(randomSignals)), randomSignals]).T, index=assetInfo.values.index, columns=["bar","gap"])
				return self.getDerivativeInfo(context, [assetInfo], [signals])

		# Calculate returns via TradeFramework
		env = SandboxEnvironment("TradeFair")
		p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
		p.addModel(RandomModel("SellAndHold", env))
		dInfo = env.handleData({}, self.asset1)

		# Calculate returns manually
		mRet =  randomSignals[:-1] * np.diff(self.asset1.values["Close"]) / self.asset1.values["Close"][:-1]

		self.assertTrue(np.allclose(dInfo.returns.values[:,1][:-1],mRet.values))

	def test_buyAndSell_multiModel(self):

		class BuyAndHoldModel(Model):
			def handleData(self, context, assetInfo):
				signals = pd.DataFrame(np.ones((len(assetInfo.values), 2)), index=assetInfo.values.index, columns=["bar","gap"])
				return self.getDerivativeInfo(context, [assetInfo], [signals])

		# randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
		randomSignals = np.array([1,1,0,-1,0,-1,1,-1,0])

		class RandomModel(Model):
			def handleData(self, context, assetInfo):
				signals = pd.DataFrame(np.array([np.zeros(len(randomSignals)), randomSignals]).T, index=assetInfo.values.index, columns=["bar","gap"])
				return self.getDerivativeInfo(context, [assetInfo], [signals])

		# Calculate returns via TradeFramework
		env = SandboxEnvironment("TradeFair")
		p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeightsOptimizer", "EqualWeights"))
		p.addModel(BuyAndHoldModel("TestModel", env))
		p.addModel(RandomModel("TestModel2", env))
		dInfo = env.handleData({}, self.asset1)

		self.assertTrue(np.allclose(dInfo.returns.values[:,1][:-1], np.array([-.2, .1, -.1, .0, -.1, .0, -.2, .0])))

	def test_kellyWeights_singleModel(self):

		# randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
		randomSignals = np.array([-1,1,-1,1,-1,1,-1,1,-1])

		class RandomModel(Model):
			def handleData(self, context, assetInfo):
				signals = pd.DataFrame(np.array([randomSignals, randomSignals]).T, index=assetInfo.values.index, columns=["bar","gap"])
				return self.getDerivativeInfo(context, [assetInfo], [signals])

		# Calculate returns via TradeFramework
		env = SandboxEnvironment("TradeFair")
		p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellylWeights"))
		p.addModel(RandomModel("TestModel", env))
		context = {}
		env.handleData(context, self.asset1)

		self.assertTrue(np.allclose(
			context["TradeFair_Portfolio"]["MyPortfolio"]["TestModel"]["dInfo"].allocations["DOW"]["gap"].values.flatten(),
			[-0.01, 0.015, -0.015, 0.0225, -0.0225, 0.03375, -0.03375, 0.050625, -0.050625]))

		self.assertTrue(np.allclose(
			context["TradeFair_Portfolio"]["MyPortfolio"]["dInfo"].values["Close"].values.flatten(),
			[1.0000000000e+00, 1.0000000000e+00,4.0000000000e+00,4.4000000000e+01,2.4200000000e+02,2.8233333333e+03,1.6940000000e+04,2.0328000000e+05,1.2705000000e+06]))

	def test_kellyWeights_multiModel(self):

		class BuyAndHoldModel(Model):
			def handleData(self, context, assetInfo):
				signals = pd.DataFrame(np.ones((len(assetInfo.values), 2)), index=assetInfo.values.index, columns=["bar","gap"])
				return self.getDerivativeInfo(context, [assetInfo], [signals])

		# randomSignals = TODO Pick random numbers between -1 and 1 and round to nearest integer.
		randomSignals = np.array([-1,1,-1,1,-1,1,-1,1,-1])

		class RandomModel(Model):
			def handleData(self, context, assetInfo):
				signals = pd.DataFrame(np.array([randomSignals, randomSignals]).T, index=assetInfo.values.index, columns=["bar","gap"])
				return self.getDerivativeInfo(context, [assetInfo], [signals])

		# Calculate returns via TradeFramework
		env = SandboxEnvironment("TradeFair")
		p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("KellyOptimizer", "KellylWeights",  opts={"window":3}))
		p.addModel(BuyAndHoldModel("TestModel", env))
		p.addModel(RandomModel("TestModel2", env))
		context = {}
		env.handleData(context, self.asset1)

		self.assertTrue(np.allclose(
			context["TradeFair_Portfolio"]["MyPortfolio"]["dInfo"].returns["Close"].values.flatten(),
			[0.0000000000e+00,0.0000000000e+00,0.0000000000e+00,2.0496382304e+16,4.0992764608e+16,2.0496382304e+16,1.3664254869e+16,4.0992764608e+16,0.0000000000e+00]))

if __name__ == '__main__':
    unittest.main()