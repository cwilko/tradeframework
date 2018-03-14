# ======================          
# Strategy Class
# ======================

class Derivative:

    def __init__(self, name, env):       
        self.name = name
        self.env = env

    def getName(self):
    	return self.name

    def handleData(self, context, assetInfo):
    	pass