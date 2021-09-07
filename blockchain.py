
from functools import reduce
# import hashlib 
import json
from collections import OrderedDict
from transaction import Transaction
# import pickle
from hash_util import hash_string_256,hash_block
from block import Block


MINING_REWARD = 10

blockchain = []
open_transaction = []
owner = "Prince"
participants = {'Prince'}



def read_data():
    global blockchain
    global open_transaction
    try:
        with open("blockchain.txt",mode="r") as f:
            saved_data = f.readlines()
            

        # blockchain = binary_content['chain']
        # open_transaction = binary_content['open_tx']

            blockchain = json.loads(saved_data[0][:-1])
            correct_blockchain = []
            
            for block in blockchain:
                shorter_tx = [Transaction(tx['sender'],tx['recipient'] ,tx['amount']) for tx in block['transactions']]
                # shorter_tx = [OrderedDict([('sender' , tx['sender']),('recipient',tx['recipient']),('amount',tx['amount']) ]) for tx in block['transactions']]
                real_block = Block(block['index'],block['previous_hash'],shorter_tx,block['nonce'],block['timestamp'])
                
                correct_blockchain.append(real_block)
            blockchain = correct_blockchain
            
            open_transaction = json.loads(saved_data[1])
            correct_transactions = []
            for tx in open_transaction:
                correct_tx = Transaction(tx['sender'],tx['recipient'] ,tx['amount'])
                # correct_tx = OrderedDict([('sender' , tx['sender']),('recipient',tx['recipient']),('amount',tx['amount']) ])
                correct_transactions.append(correct_tx)


            open_transaction = correct_transactions
            # binary_content = pickle.loads(f.read())
            # print(binary_content)
            

        
    except (IOError,IndexError):
        # genesis_block = {
        #         'previous_hash': '',
        #         'index':0,
        #         'transactions':[] ,
        #         'nonce': 200
        #                 }
        genesis_block = Block(0,'',[],200,0)
        blockchain = [genesis_block]
        open_transaction = []
        
        # print(blockchain[0].__dict__)
        
        
    
read_data()


def save_data():
    try:
        with open("blockchain.txt",mode="w") as f:
            # dict_chain = [block.__dict__ for block in blockchain]
            print(blockchain)
            dict_chain = [block.__dict__ for block in [Block(child_block.index,child_block.previous_hash,[tx.__dict__ for tx in child_block.transactions],child_block.nonce,child_block.timestamp) for child_block in blockchain] ]
            f.write(json.dumps(dict_chain))
            f.write("\n")
            f.write(json.dumps(open_transaction))
            # pickled_data = {
            #     'chain': blockchain,
            #     'open_tx': open_transaction
            # }
            # f.write(pickle.dumps(pickled_data))
        
    except IOError:
        print("Failed to persisit data")
      
    


# def hash_block(block):
#     return hash_string_256(json.dumps(block,sort_keys=True).encode())


def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None
    return blockchain[-1]
 

def verify_transaction(transaction):
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount


def add_transaction(recipient,sender=owner,amount=1.0):
    # transaction = {
    #     'sender':sender,
    #     'recipient':recipient,
    #     'amount': amount
    # }
    transaction = Transaction(sender,recipient,amount)
    if(verify_transaction(transaction)):
        open_transaction.append(transaction)
        # participants.add(sender)
        # participants.add(recipient)
        save_data()
        return True
    else:
        return False


def valid_proof(transactions,previous_hash,proof):
    guess = str([tx.ordered_dict() for tx in transactions]) + str(previous_hash) + str(proof)

    guess_hash = hash_string_256(guess.encode())
    print(guess_hash)
    return guess_hash[0:2] == '11'


def proof_of_work():
    last_block = blockchain[-1]
    prev_hash = hash_block(last_block)
    nonce = 0
    while not valid_proof(open_transaction,prev_hash,nonce):
        nonce += 1
    return nonce




def get_balance(participant):
    tx_sender = [[tx.amount 
                for tx in block.transactions 
                if tx.sender == participant] 
                for block in blockchain]
    

    open_tx_sender = [tx.amount for tx in open_transaction if tx.sender == participant]
    tx_sender.append(open_tx_sender)
                
   
    amount_sent = reduce(lambda tx_sum,tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum ,tx_sender,0)
    # amount_sent = 0
    # for tx in tx_sender:
    #     if(len(tx) > 0):
    #         amount_sent += tx[0]

    tx_recipient = [[tx.amount
                for tx in block.transactions 
                if tx.recipient == participant] 
                for block in blockchain]
    amount_received = reduce(lambda tx_sum,tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum ,tx_recipient,0)
    # for tx in tx_recipient:
    #     if(len(tx) > 0):
    #         amount_received += tx[0]
    

    return amount_received - amount_sent


def verify_chain():
    for (index,block) in enumerate(blockchain):
        if index == 0: 
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block.transactions[:-1],block.previous_hash,block.nonce):
            print("Proof of Work is Invalid")
            return False
        
    return True


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    nonce = proof_of_work()

    # reward_transaction = {
    #     'sender':"SYSTEM",
    #     'recipient':owner,
    #     'amount':MINING_REWARD
    # }

    # reward_transaction = OrderedDict([('sender' , 'SYSTEM'),('recipient',owner),('amount',MINING_REWARD)])
    reward_transaction = Transaction('SYSTEM',owner,MINING_REWARD)
    copy_transactions = open_transaction[:]
    copy_transactions.append(reward_transaction)
    # open_transaction.append(reward_transaction)
    block = Block(len(blockchain),hashed_block,copy_transactions,nonce)
    # block = {
    # 'previous_hash': hashed_block,
    # 'index':len(blockchain),
    # 'transactions':copy_transactions,
    # 'nonce': nonce
    # }
    blockchain.append(block)
    # save_data()
    return True

            

def get_transaction_value():
    tx_recipient = input("Enter the recipient: ")
    tx_amount =  float(input("Please enter transaction amount: "))

    return tx_recipient,tx_amount


def get_user_choice():
    return input("Please enter your choice: ")


def print_blockchain():
    for block in blockchain:
        print("Consoling the block")
        print(block)

    



while True:
    print("Please Choose")
    print("1: Add a new transaction value ")
    print("2: Mine a new Block ")
    print("3: Output the blockchains and exit ")
    print("4: Output the Participants ")
    
    print("q: Quit")



    user_choice = get_user_choice();
    if user_choice == '1':
        recipient,amount = get_transaction_value();
        if add_transaction(recipient,amount=amount):
            print("Transaction done successfully")
        else:
            print("Transaction Failed!!!!")
        

    elif user_choice == '2':
      
        
        
        if mine_block():
            open_transaction = []
            save_data()
    
    elif user_choice == '3':
        print_blockchain()

    elif user_choice == '4':
        print(participants)


   

    elif user_choice == 'q':
        break

    else:
        print("The input given is invalid")
        break

    if not verify_chain():
        print("The chain is invalid")
        break


    print("the sender is Prince")
    print("The Balance of {} is {:5.1f} ".format("Prince",get_balance('Prince')))

    


