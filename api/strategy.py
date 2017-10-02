# ======================          
# Strategy Class
# ======================

class Strategy:

    def __init__(self, name, env):  
    	self.index = 0      
        self.name = name
        self.env = env

        # Create a simple trader for tracking base returns
        self.tEngine = env.createTradeEngine(self.name)


    def getName(self):
    	return self.name

    def handleData(self, context, data, index):
    	self.index = index