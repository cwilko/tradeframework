import numpy as np
import pandas as pd
import uuid
import copy as cp

# ======================
# Asset Class
# ======================


class Asset:

    def __init__(self, name, values=pd.DataFrame(), returns=pd.DataFrame(), env=None):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.values = values
        self.returns = returns
        self.env = env

    def __str__(self):
        return ''.join(['{ "id": "', self.uuid, '", "name": "', self.name, '", "type": "', str(type(self)), '"}'])

    def getName(self):
        return self.name

    def getId(self):
        return self.uuid

    def getValues(self):
        return self.values

    def getAllocations(self):
        return None

    def append(self, asset):
        self.values = asset.values.combine_first(self.values)
        return self

    def findAsset(self, assetName):
        return None

    def refresh(self, idx):
        return self.updateState(None, idx)

    def updateState(self, weights, idx):
        returns = self.env.tradeEngine.calculateReturns(self, idx)
        self.returns = returns.combine_first(self.returns)
        return self
