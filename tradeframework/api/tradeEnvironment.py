# ======================
# TradeEnvironment Class
# ======================

from . import AssetStore, Derivative, Asset
import tradeframework.optimizers as opt
import tradeframework.models as md
import pandas as pd
import uuid


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

    def getPortfolio(self):
        if not self.portfolio:
            raise Exception('Error: No portfolio has been configured for this environment.')
        else:
            return self.portfolio

    def setPortfolio(self, derivative):
        self.portfolio = derivative
        return self.portfolio

    def createDerivative(self, name, weightGenerator=None):
        return Derivative(name, self, weightGenerator=weightGenerator)

    def createAsset(self, name, values=pd.DataFrame()):
        return self.append(Asset(name, values=values, env=self), refreshPortfolio=False)

    def createAssets(self, marketData):
        return [self.createAsset(name, marketData.xs(name, level="mID")) for name in marketData.index.get_level_values("mID").unique().values]

    def createModel(self, modelClass, opts={}):
        modelInstance = getattr(md, modelClass)
        model = modelInstance(self, **opts)
        return model

    def createOptimizer(self, optClass, opts={}):
        optInstance = getattr(opt, optClass)
        optimizer = optInstance(self, **opts)
        return optimizer

    def refresh(self, idx=0, copy=False):
        if not self.portfolio:
            raise Exception('Error: No portfolio has been configured for this environment.')

        # Mediate between our Portfolio and the Environment
        portfolio = self.portfolio
        if copy:
            portfolio = portfolio.copy()
        return portfolio.refresh(idx)

    def append(self, asset, refreshPortfolio=False):
        storedAsset = self.assetStore.append(asset)
        storedAsset.env = self  # For backwards compatibility. TODO: migrate to createAsset()
        if refreshPortfolio:
            self.portfolio.refresh(asset.values.index[0])
        return storedAsset
