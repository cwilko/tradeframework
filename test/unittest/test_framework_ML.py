import unittest
import os
import pandas as pd
import numpy as np
from tradeframework.api import Asset
from tradeframework.environments import SandboxEnvironment
import tradeframework.operations.utils as utils
from quantutils.api.auth import CredentialsStore

dir = os.path.dirname(os.path.abspath(__file__))


class FrameworkTest(unittest.TestCase):

    def setUp(self):
        ts = pd.read_csv(dir + '/data/testDOW.csv', parse_dates=True, index_col=0, dayfirst=True)
        #ts = ts.tz_localize("UTC")
        ts.index = ts.index.tz_convert("US/Eastern")
        self.asset1 = Asset("DOW", ts)

    def test_MIBasic_singleModel(self):

        TRAINING_RUN_ID = "94b227b9d7b22c920333aa36d23669c8"
        DATASET_ID = "4234f0f1b6fcc17f6458696a6cdf5101"

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeights", "EqualWeightsOptimizer"))
        env.setPortfolio(p)
        p.addAsset(env.createModel("Test-MIBasicModel", "MIBasicModel", opts={'credstore': CredentialsStore(), 'dataset_id': DATASET_ID, 'training_run_id': TRAINING_RUN_ID, 'threshold': 0}))

        env.append(Asset("DOW", self.asset1.values))

        # Check results
        self.assertTrue(np.allclose(np.prod(utils.getPeriodReturns(p.returns) + 1), 0.9941924543457394))

    def test_MIBasic_singleModel_online(self):

        TRAINING_RUN_ID = "94b227b9d7b22c920333aa36d23669c8"
        DATASET_ID = "4234f0f1b6fcc17f6458696a6cdf5101"

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeights", "EqualWeightsOptimizer"))
        env.setPortfolio(p)
        p.addAsset(env.createModel("Test-MIBasicModel", "MIBasicModel", opts={'credstore': CredentialsStore(), 'dataset_id': DATASET_ID, 'training_run_id': TRAINING_RUN_ID, 'threshold': 0}))

        # Extract 3pm indices
        # crop = ppl.cropTime(asset1.values, "15:00", "16:00")
        # idx = [asset1.values.index.get_loc(crop.index[x]) for x in range(len(crop))]
        idx = [19, 42, 44, 67, 90]

        c = 0
        for i in idx:
            env.append(Asset("DOW", self.asset1.values[c:i]))
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))
            c = i + 1
        env.append(Asset("DOW", self.asset1.values[c:]))

        # Check results
        self.assertTrue(np.allclose(np.prod(utils.getPeriodReturns(p.returns) + 1), 0.9941924543457394))

    def test_MIBasic_multiModel(self):

        TRAINING_RUN_ID = "94b227b9d7b22c920333aa36d23669c8"
        DATASET_ID1 = "4234f0f1b6fcc17f6458696a6cdf5101"
        DATASET_ID2 = "3231bbe5eb2ab84eb54c9b64a8dcea55"

        agg = [{
            'training_run_id': TRAINING_RUN_ID,
            'datasets': [DATASET_ID1, DATASET_ID2]
        }]

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeights", "EqualWeightsOptimizer"))
        env.setPortfolio(p)
        p.addAsset(env.createModel("Test-MIAggregateModel", "MIAggregateModel", opts={'credstore': CredentialsStore(), 'mi_models': agg, 'aggMethod': 'vote_unanimous_all', 'threshold': 0}))

        env.append(Asset("DOW", self.asset1.values))

        print(np.prod(utils.getPeriodReturns(p.returns) + 1))
        # Check results
        self.assertTrue(np.allclose(np.prod(utils.getPeriodReturns(p.returns) + 1), 0.9979433892004727))

    def test_MIBasic_multiModel_online(self):

        TRAINING_RUN_ID = "94b227b9d7b22c920333aa36d23669c8"
        DATASET_ID1 = "4234f0f1b6fcc17f6458696a6cdf5101"
        DATASET_ID2 = "3231bbe5eb2ab84eb54c9b64a8dcea55"

        agg = [{
            'training_run_id': TRAINING_RUN_ID,
            'datasets': [DATASET_ID1, DATASET_ID2]
        }]

        # Calculate returns via TradeFramework
        env = SandboxEnvironment("TradeFair")
        p = env.createPortfolio("MyPortfolio", optimizer=env.createOptimizer("EqualWeights", "EqualWeightsOptimizer"))
        env.setPortfolio(p)
        p.addAsset(env.createModel("Test-MIAggregateModel", "MIAggregateModel", opts={'credstore': CredentialsStore(), 'mi_models': agg, 'aggMethod': 'vote_unanimous_all', 'threshold': 0}))

        # Extract 3pm indices
        # crop = ppl.cropTime(asset1.values, "15:00", "16:00")
        # idx = [asset1.values.index.get_loc(crop.index[x]) for x in range(len(crop))]
        idx = [19, 42, 44, 67, 90]

        c = 0
        for i in idx:
            env.append(Asset("DOW", self.asset1.values[c:i]))
            env.append(Asset("DOW", self.asset1.values[i:i + 1]))
            c = i + 1
        env.append(Asset("DOW", self.asset1.values[c:]))

        print(np.prod(utils.getPeriodReturns(p.returns) + 1))

        # Check results
        self.assertTrue(np.allclose(np.prod(utils.getPeriodReturns(p.returns) + 1), 0.9979433892004727))

if __name__ == '__main__':
    unittest.main()
