from time import time
from helpers.printable import Printable
class Block(Printable):
    def __init__(self,index,previous_hash,transactions,nonce,time=time()):
        
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.nonce = nonce
        self.timestamp = time
    

    def __repr__(self):
        # return f"""
        # Index: {self.index} ,
        # Transactions: {self.transactions} 
        # previous_hash: {self.previous_hash} , 
        # nonce: {self.nonce} , 
        # timestamp: {self.timestamp}
        # """
        return str(self.__dict__)
