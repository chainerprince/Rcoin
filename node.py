from uuid import uuid4
from wallet import Wallet
from helpers.verification import Verify
from blockchain import Blockchain

class Node:
    def __init__(self):
        self.wallet = Wallet()
        # self.blockchain = None
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        tx_recipient = input("Enter the recipient: ")
        tx_amount =  float(input("Please enter transaction amount: "))
        return tx_recipient,tx_amount


    def get_user_choice(self):
        return input("Please enter your choice: ")

    def print_blockchain(self):
        for block in self.blockchain.chain:
            print("Consoling the block")
            print(block)


    def get_input(self):
        while True:
            print("Please Choose")
            print("1: Add a new transaction value ")
            print("2: Mine a new Block ")
            print("3: Output the blockchains and exit ")
            print("4: Create a Wallet ")
            print("5: Store Keys to a wallet")
            print("6: Load keys from the wallet")
            print("q: Quit")



            user_choice = self.get_user_choice();
            if user_choice == '1':
                recipient,amount = self.get_transaction_value();
                signature = self.wallet.sign_tx(self.wallet.public_key,recipient,amount)
                if self.blockchain.add_transaction(recipient,self.wallet.public_key,signature,amount=amount):
                    print("Transaction done successfully")
                else:
                    print("Transaction Failed!!!!")
                print(self.blockchain.get_open_tx())


            elif user_choice == '2':
                 self.blockchain.mine_block()
            
            elif user_choice == '3':
                if not self.print_blockchain(self.blockchain):
                    print("The Mining Failed because NO WAllet")
                

            # elif user_choice == '4':
            #     print(participants)


            elif user_choice == '4':  
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_choice == '5':
                self.wallet.save_keys()

            elif user_choice == '6':  
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_choice == 'q':
                break
            
            else:
                print("The input given is invalid")
                break
            # verifi = Verify()
            if not Verify.verify_chain(self.blockchain.chain):
                print("The chain is invalid")
                break
            
            
            # print("the sender is Prince")
            print("The Balance of {} is {:5.1f} ".format(self.wallet.public_key,self.blockchain.get_balance()))




# if __name__ == 'main':
#     node = Node()
#     node.get_input()


node = Node()
node.get_input()







