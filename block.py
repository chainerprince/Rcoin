from time import time
class Block:
    def __init__(self,index,previous_hash,transactions,nonce,time=time()):
        
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.nonce = nonce
        self.timestamp = time
