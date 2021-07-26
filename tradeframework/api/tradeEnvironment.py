# ======================
# TradeEnvironment Class
# ======================

from . import Portfolio, AssetStore
import tradeframework.optimizers as opt
import tradeframework.models as md
import uuid


class TradeEnvironment():

    def __init__(self, name):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.assetStore = AssetStore()
        return

    def __str__(self):
        return ''.join(['{ "id": "', self.uuid, '", "name": "', self.name, '", "type": "', str(type(self)), '", "portfolio": ', str(self.portfolio), ' }'])

    def getId(self):
        return self.uuid

    def getName(self):
        return self.name

    def getAssetStore(self):
        return self.assetStore

    def getPortfolio(self):
        if not self.portfolio:
            raise Exception('Error: No portfolio has been configured for this environment.')
        else:
            return self.portfolio

    def setPortfolio(self, portfolio):
        self.portfolio = portfolio
        return portfolio

    def createPortfolio(self, name, optimizer=None):
        return Portfolio(name, self, optimizer)

    def createModel(self, name, modelClass, args=()):
        modelInstance = getattr(md, modelClass)
        model = modelInstance(name, self, *args)
        return model

    def createOptimizer(self, name, optClass, opts={}):
        optInstance = getattr(opt, optClass)
        optimizer = optInstance(name, self, **opts)
        return optimizer

    def append(self, asset):
        if not self.portfolio:
            raise Exception('Error: No portfolio has been configured for this environment.')
