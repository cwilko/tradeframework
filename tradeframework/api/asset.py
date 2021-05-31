import numpy as np
import pandas as pd

# ======================
# Asset Class
# ======================


class Asset:

    # TODO: Centralised storage of underlying assets in an Asset Store on the env?
    def __init__(self, name, values=None):
        self.name = name
        self.values = values

    def getName(self):
        return self.name

    def getValues(self):
        return self.values

    def getUnderlyingAllocations(self):
        return pd.DataFrame(np.ones((len(self.values), 2)), columns=[
            [self.name, self.name], ['bar', 'gap']], index=self.values.index)

    # TODO: Centralised storage of underlying assets in an Asset Store on the env?
    def append(self, asset):
        if self.values is None:
            self.values = asset.values
        else:
            self.values = asset.values.combine_first(self.values)
        return self
