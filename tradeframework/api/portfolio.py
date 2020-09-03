from . import Derivative

# ======================
# Portfolio Class
# ======================


class Portfolio(Derivative):

    def __init__(self, name, env, optimizer=None):
        Derivative.__init__(self, name, env)
        if (optimizer is None):
            self.optimizer = env.createOptimizer(
                "EqualWeightsOptimizer", self.name)
        else:
            self.optimizer = optimizer

    def addPortfolio(self, name, optimizer=None):
        portfolio = Portfolio(name, self.env, optimizer)
        self.assets.append(portfolio)
        return portfolio

    def addModel(self, model):
        self.assets.append(model)
        return model

    def handleData(self, asset):

        # Update all children
        derivatives = [derivative.handleData(asset) for derivative in self.assets]

        # Calculate portfolio allocation
        weights = self.optimizer.getWeights([derivative.returns for derivative in derivatives])

        # Update derivative state
        return self.update(derivatives, weights)
