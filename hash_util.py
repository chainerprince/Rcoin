import json
import hashlib

def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()

def hash_block(block):
    dict_blocks = block.__dict__.copy()
    dict_blocks['transactions'] = [tx.ordered_dict() for tx in dict_blocks['transactions']]
    
    return hash_string_256(json.dumps(dict_blocks,sort_keys=True).encode())