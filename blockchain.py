
from functools import reduce
# import hashlib 
import json
from wallet import Wallet
# from collections import OrderedDict
from transaction import Transaction
# import pickle

import requests


from helpers.hash_util import hash_block
from block import Block
from helpers.verification import Verify


MINING_REWARD = 10




class Blockchain:
    def __init__(self,public_key,node_id):
        genesis_block = Block(0,'',[],200,0)
        self.chain  = [genesis_block]
        self.__open_transactions = []
        self.public_key = public_key
        self.__nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.read_data()

    @property 
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self,val):
        self.__chain = val


    def get_chain(self):
        return self.__chain[:]


    def get_open_tx(self):
        return self.__open_transactions[:]


    def read_data(self):
        
        
        try:
            with open("blockchain.txt_{}".format(self.node_id),mode="r") as f:
                saved_data = f.readlines()
                

            # blockchain = binary_content['chain']
            # open_transaction = binary_content['open_tx']

                blockchain = json.loads(saved_data[0][:-1])
                correct_blockchain = []
                
                for block in blockchain:
                    shorter_tx = [Transaction(tx['sender'],tx['recipient'],tx['signature'] ,tx['amount']) for tx in block['transactions']]
                    # shorter_tx = [OrderedDict([('sender' , tx['sender']),('recipient',tx['recipient']),('amount',tx['amount']) ]) for tx in block['transactions']]
                    real_block = Block(block['index'],block['previous_hash'],shorter_tx,block['nonce'],block['timestamp'])
                    
                    correct_blockchain.append(real_block)
                self.chain = correct_blockchain
                
                open_transaction = json.loads(saved_data[1][:-1])
                correct_transactions = []
                for tx in open_transaction:
                    correct_tx = Transaction(tx['sender'],tx['recipient'] ,tx['signature'],tx['amount'])
                    # correct_tx = OrderedDict([('sender' , tx['sender']),('recipient',tx['recipient']),('amount',tx['amount']) ])
                    correct_transactions.append(correct_tx)


                self.__open_transactions = correct_transactions
                self.__nodes = set(json.loads(saved_data[2]))

                # binary_content = pickle.loads(f.read())
                # print(binary_content)
                

            
        except (IOError,IndexError):
            print("Some Error in loading file")

            
            
            # print(blockchain[0].__dict__)
            
            
        



    def save_data(self):
        try:
            with open("blockchain.txt_{}".format(self.node_id),mode="w") as f:
                # dict_chain = [block.__dict__ for block in blockchain]
                # print(blockchain)
                dict_chain = [block.__dict__ for block in [Block(child_block.index,child_block.previous_hash,[tx.__dict__ for tx in child_block.transactions],child_block.nonce,child_block.timestamp) for child_block in self.__chain] ]
                f.write(json.dumps(dict_chain))
                f.write("\n")
                dict_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(dict_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__nodes)))
                # pickled_data = {
                #     'chain': blockchain,
                #     'open_tx': open_transaction
                # }
                # f.write(pickle.dumps(pickled_data))
            
        except IOError:
            print("Failed to persisit data")
      
    


# def hash_block(block):
#     return hash_string_256(json.dumps(block,sort_keys=True).encode())


    def get_last_blockchain_value(self):
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]
 



    def add_transaction(self,recipient,sender,signature,amount=1.0,is_receiving=False):
        if self.public_key == None:
            print("The public key has problems")
            return False
        transaction = Transaction(sender,recipient,signature,amount)
        

        # if not Wallet.verify_signature(transaction):
        #     return False
        
        if(Verify.verify_transaction(transaction,self.get_balance)):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        res = requests.post(url,json={'sender':sender,'recipient':recipient,'amount':amount,'signature':signature})
                        if res.status_code == 400 or res.status_code == 500:
                            print(node)
                            print("The transaction failed")
                            return False
                    except requests.exceptions.ConnectionError :
                        print("The node is down")
                        continue
                   
                
            return True
        else:
            print("Verification failed")
            return False


    def proof_of_work(self):
        last_block = self.__chain[-1]
        prev_hash = hash_block(last_block)
        nonce = 0
        
        while not Verify.valid_proof(self.__open_transactions,prev_hash,nonce):
            nonce += 1
        return nonce




    def get_balance(self,sender=None):
        
        if sender == None:
            if self.public_key == None:
                return None                
            participant = self.public_key
        else:
            participant = sender
        
        # print("The participant who made this ",participant)
        tx_sender = [[tx.amount 
                    for tx in block.transactions 
                    if tx.sender == participant] 
                    for block in self.__chain]
        # print("the tx sender",tx_sender)
        

        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
                    
    
        amount_sent = reduce(lambda tx_sum,tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum ,tx_sender,0)

        tx_recipient = [[tx.amount
                    for tx in block.transactions 
                    if tx.recipient == participant] 
                    for block in self.__chain]
        print("the recipient",tx_recipient)
        amount_received = reduce(lambda tx_sum,tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum ,tx_recipient,0)
        

        return amount_received - amount_sent





    def mine_block(self):
        if self.public_key == None:
            return False
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        nonce = self.proof_of_work()

        reward_transaction = Transaction('SYSTEM',self.public_key,'',MINING_REWARD)
        copy_transactions = self.__open_transactions[:]
        for tx in copy_transactions:
            if not Wallet.verify_signature(tx):
                return False

        copy_transactions.append(reward_transaction)
        # open_transaction.append(reward_transaction)
        block = Block(len(self.__chain),hashed_block,copy_transactions,nonce)
        
        
        self.__chain.append(block)
        self.__open_transactions = []
        # print(self.__nodes)
        self.save_data()
        for node in self.__nodes:
            url = 'http://{}/broadcast-block'.format(node)
        
            correct_block = block.__dict__.copy()
            correct_block['transactions'] = [tx.__dict__ for tx in correct_block['transactions']]
            
            try:
                res = requests.post(url,json={'block':correct_block})
                if res.status_code == 400 or res.status_code == 500:                    
                    print("Block broadcasting failed we need to resolve")
                    return False
                
                if res.status_code == 409:
                    self.resolve_conflicts = True

            except requests.exceptions.ConnectionError:
                print("The node is down")
                continue
        return block

    
    def add_block(self,block):
        transactions = [Transaction(tx['sender'],tx['recipient'],tx['signature'] ,tx['amount']) for tx in block['transactions']]
        valid_proof = Verify.valid_proof(transactions[:-1],block['previous_hash'],block['nonce'])
        correct_hash = hash_block(self.chain[-1]) == block['previous_hash']
        
        
        if not valid_proof or not correct_hash:
            print("The proof is invalid")
            return False
        obj_block = Block(block['index'],block['previous_hash'],transactions,block['nonce'],block['timestamp'])
        self.__chain.append(obj_block)
        saved_tx = self.__open_transactions[:]
        for tx in block['transactions']:
            for opentx in saved_tx:
                if opentx.sender == tx['sender'] and opentx.recipient == tx['recipient'] and opentx.amount == tx['amount'] and opentx.signature == tx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print("Item was already removed")
                    
                    
        self.save_data()
        return True



    def resolve_conflict(self):
        honest_chain = self.chain
        replaced = False
        for node in self.__nodes:
            url = f"http://{node}/chain"
            try:
                res = requests.get(url)
                chain_node = res.json()
                chain_node = [Block(block['index'],block['previous_hash'],[Transaction(tx['sender'],tx['recipient'],tx['signature'],tx['amount']) for tx in block['transactions']],block['nonce'],block['timestamp'] ) for block in chain_node]
                
                if (len(chain_node) > len(self.chain)) and Verify.verify_chain(chain_node):
                    honest_chain = chain_node
                    replaced = True


            except requests.ConnectionError:
                continue


            self.resolve_conflicts = False
            self.chain = honest_chain
            if replaced:
                self.__open_transactions = []

            self.save_data()
            return replaced



    def add_node(self,node):
        self.__nodes.add(node)
        self.save_data()

    def remove_node(self,node):
        self.__nodes.discard(node)
        self.save_data()


    def get_nodes(self):
        return list(self.__nodes)
        

            







