# ======================
# AssetStore Class
# ======================


class AssetStore:

    def __init__(self):
        self.store = {}

    def getAsset(self, name):
        return self.store.get(name)

    def addAsset(self, asset):
        self.store[asset.getName()] = asset
        return asset

    def append(self, asset):
        storedAsset = self.getAsset(asset.getName())
        if (storedAsset):
            storedAsset.append(asset)
        else:
            storedAsset = self.addAsset(asset)
        return storedAsset
