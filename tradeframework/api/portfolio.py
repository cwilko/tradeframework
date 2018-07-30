from . import Derivative

# ======================          
# Portfolio Class
# ======================

class Portfolio(Derivative):

    def __init__(self, name, env, optimizer=None):
        Derivative.__init__(self, name, env)
        if (optimizer is None):
            self.optimizer = env.createOptimizer("EqualWeightsOptimizer", self.name)
        else:
            self.optimizer = optimizer
        self.derivative_list = []        

    def createPortfolio(self, name, optimizer=None):
        portfolio = Portfolio(name, self.env, optimizer)
        self.derivative_list.append(portfolio)
        return portfolio

    def addModel(self, model):
        self.derivative_list.append(model)
        return model

    def handleData(self, context, assetInfo ):
        Derivative.handleData(self, context, assetInfo)

        # Create context space
        if self.name not in context:
            context[self.name] = {}
        
        # Update all children
        derivInfos = [derivative.handleData(context[self.name], assetInfo) for derivative in self.derivative_list]

        # Calculate portfolio allocation
        weights = self.optimizer.getWeights(context[self.name], [dInfo.returns for dInfo in derivInfos])  

        # Calculate portfolio values
        # dInfo = 

        # Get allocations for each underlying asset
        # TODO : Possibly do this outside of this function.
        # uAllocations = 

        # Merge underlying asset allocations
        # TODO : Base this off uAllocations. Possibly do this outside of this function.
        #Allocations = reduce(lambda x, y: x.add(y, fill_value=0), dAllocations) 

        # Return portfolio allocations
        return self.getDerivativeInfo(context, derivInfos, weights)