import numpy as np
import pandas as pd

# ======================
# Asset Class
# ======================


class Asset:

    def __init__(self, name, values=[]):
        self.name = name
        self.values = values

    def getName(self):
        return self.name

    def getValues(self):
        return self.allocations

    def getUnderlyingAllocations(self):
        return pd.DataFrame(np.ones((len(self.values), 2)), columns=[
            [self.name, self.name], ['bar', 'gap']], index=self.values.index)
