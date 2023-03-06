# ======================
# TradeEnvironment Class
# ======================

from . import AssetStore, Derivative, Asset
import pandas as pd
import uuid
import copy as cp
import importlib


class TradeEnvironment():

    def __init__(self, name, tz):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.assetStore = AssetStore()
        self.tz = tz
        return

    def __str__(self):
        return ''.join(['{ "id": "', self.uuid, '", "name": "', self.name, '", "type": "', str(type(self)), '", "portfolio": ', str(self.portfolio), ' }'])

    def getId(self):
        return self.uuid

    def getName(self):
        return self.name

    def getAssetStore(self):
        return self.assetStore

    def getTimezone(self):
        return self.tz

    def copy(self):
        env = cp.deepcopy(self)
        env.uuid = str(uuid.uuid4())
        env.name = env.name + "_copy"
        return env

    def getPortfolio(self):
        if not self.portfolio:
            raise Exception('Error: No portfolio has been configured for this environment.')
        else:
            return self.portfolio

    def setPortfolio(self, derivative):
        self.portfolio = derivative
        return self.portfolio

    def findAsset(self, assetName):
        if assetName == self.getPortfolio().getName():
            return self.getPortfolio()
        result = self.getPortfolio().findAsset(assetName)
        if not result:
            raise Exception('Error: Asset, {0}, not found in portfolio {1}'.format(assetName, self.getName()))
        return result

    def createDerivative(self, name, weightGenerator=None):
        return Derivative(name, self, weightGenerator=weightGenerator)

    def createAsset(self, name, values=pd.DataFrame()):
        return self.append(Asset(name, values=values, env=self), refreshPortfolio=False)

    def createAssets(self, marketData):
        return [self.createAsset(name, marketData.xs(name, level="mID")) for name in marketData.index.get_level_values("mID").unique().values]

    def createModel(self, modelClass, modelModule="tradeframework.models", opts={}):
        module = importlib.import_module(modelModule)
        modelInstance = getattr(module, modelClass)
        model = modelInstance(self, **opts)
        return model

    def createOptimizer(self, optClass, optModule="tradeframework.optimizers", opts={}):
        module = importlib.import_module(optModule)
        optInstance = getattr(module, optClass)
        optimizer = optInstance(self, **opts)
        return optimizer

    def refresh(self, idx=0):
        if not self.portfolio:
            raise Exception('Error: No portfolio has been configured for this environment.')

        return self.portfolio.refresh(idx)

    def append(self, asset, refreshPortfolio=False):
        storedAsset = self.assetStore.append(asset)
        storedAsset.env = self  # For backwards compatibility. TODO: migrate to createAsset()
        if refreshPortfolio:
            self.portfolio.refresh(asset.values.index[0])
        return storedAsset
