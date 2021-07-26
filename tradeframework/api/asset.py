import numpy as np
import pandas as pd

# ======================
# Asset Class
# ======================


class Asset:

    def __init__(self, name, values=None):
        self.name = name
        self.values = values

    def __str__(self):
        return ''.join(['{ "name": "', self.name, '", "type": "', str(type(self)), '" }'])

    def getName(self):
        return self.name

    def getValues(self):
        return self.values

    # TODO : Could implement pip here
    def getUnderlyingAllocations(self):
        return pd.DataFrame(np.ones((len(self.values), 2)), columns=[
            [self.name, self.name], ['bar', 'gap']], index=self.values.index)

    def append(self, asset):
        if self.values is None:
            self.values = asset.values
        else:
            self.values = asset.values.combine_first(self.values)
        return self
