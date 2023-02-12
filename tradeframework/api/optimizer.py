from . import WeightGenerator

# ======================
# Optimizer Class
# ======================


class Optimizer(WeightGenerator):

    def __init__(self, env):
        self.env = env

    def generateWeights(self, derivatives, idx):
        return self.getWeights([derivative.returns for derivative in derivatives], idx)
