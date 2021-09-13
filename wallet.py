# from Crypto import PublicKey
# from transaction import Transaction
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random as rand
import binascii
# from Crypto import *
class Wallet:
    def __init__(self,node_id):
        
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self):
        private_key,public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

        
    
    def save_keys(self):
        if self.private_key != None and self.public_key != None:
            try:
                with open('keys_{}.txt'.format(self.node_id),'w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)  
                    return True          
            except (IOError,IndexError):
                print("The file is empty")
                return False


    def load_keys(self):
        try:
            with open('keys_{}.txt'.format(self.node_id),'r') as f:
                keys = f.readlines();
                public_key = keys[0][:-1]
                private_key = keys[1]

                self.public_key = public_key
                self.private_key = private_key
                return True
            
        except (IOError,IndexError):
            print("The file is empty or out of bound")
            return False

        
            

    


    def generate_keys(self):
        private_key = RSA.generate(1024,rand.new().read)
        public_key = private_key.public_key()

        return (binascii.hexlify(private_key.export_key(format="DER")).decode('ascii'),binascii.hexlify(public_key.export_key(format="DER")).decode('ascii'))



    def sign_tx(self,sender,recipient,amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        payload_hash = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(payload_hash)
        return binascii.hexlify(signature).decode('ascii')


    @staticmethod
    def verify_signature(tx):
        
        public_key = RSA.importKey(binascii.unhexlify(tx.sender))
        verifier = PKCS1_v1_5.new(public_key)
        payload_hash = SHA256.new( (str(tx.sender) + str(tx.recipient) + str(tx.amount)).encode('utf8'))
        return verifier.verify(payload_hash,binascii.unhexlify(tx.signature))

        
            

        




        