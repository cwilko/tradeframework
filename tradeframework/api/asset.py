import numpy as np
import pandas as pd
import uuid
import copy as cp

# ======================
# Asset Class
# ======================


class Asset:

    def __init__(self, name, values=None):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.values = values
        if values is None:
            self.values = pd.DataFrame()

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
        if self.values is None:
            self.values = asset.values
        else:
            self.values = asset.values.combine_first(self.values)
        return self

    def copy(self):
        asset = cp.deepcopy(self)
        asset.uuid = str(uuid.uuid4())
        asset.name = asset.name + "_copy"
        return asset

    def findAsset(self, assetName):
        return None

    def refresh(self, idx):
        pass
