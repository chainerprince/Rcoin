from wallet import Wallet
from helpers.hash_util import hash_string_256,hash_block
class Verify:
    @staticmethod
    def verify_transaction(transaction,get_balance,check_balance=True):

        if check_balance:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_signature(transaction)

    @staticmethod
    def valid_proof(transactions,previous_hash,proof):
        guess = str([tx.ordered_dict() for tx in transactions]) + str(previous_hash) + str(proof)

        guess_hash = hash_string_256(guess.encode())
        # print(guess_hash)
        return guess_hash[0:2] == '11'

    @classmethod
    def verify_chain(cls,blockchain):
        for (index,block) in enumerate(blockchain):
            if index == 0: 
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1],block.previous_hash,block.nonce):
                print("Proof of Work is Invalid")
                return False

            return True

    @classmethod
    def verify_transactions(cls,open_transaction,get_balance):
        return all([cls.verify_transaction(tx,get_balance,False) for tx in open_transaction])
