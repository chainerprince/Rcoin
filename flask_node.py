# import json
from argparse import ArgumentParser
from flask import Flask,jsonify,request,render_template
from wallet import Wallet
from blockchain import Blockchain
app = Flask(__name__)




@app.route("/")
def index():
    return render_template('node.html')
    

@app.route('/wallet',methods=["POST"])
def create_wallet():
    wallet.create_keys()
    if wallet.save_keys():
        res = {
            'public_key' : wallet.public_key,
            'private_key' : wallet.private_key
        }
        global blockchain
        blockchain = Blockchain(wallet.public_key,port)
        res = {
            'public_key' : wallet.public_key,
            'private_key' : wallet.private_key,
            'balance': blockchain.get_balance()
        }
        return jsonify(res),201
    else:
        res = {
            "msg": "Saving the keys failed"
        }
        return jsonify(res), 500


@app.route('/wallet',methods=["GET"])
def load_wallet():
    wallet.load_keys()
    if wallet.load_keys():
        res = {
            'public_key' : wallet.public_key,
            'private_key' : wallet.private_key
        }
        global blockchain
        blockchain = Blockchain(wallet.public_key,port)
        res = {
            'public_key' : wallet.public_key,
            'private_key' : wallet.private_key,
            'balance': blockchain.get_balance()
        }
        return jsonify(res),201
    else:
        res = {
            "msg": "Loading the keys failed"
        }
        return jsonify(res), 500




@app.route('/balance',methods=["GET"])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        res = {
            "msg":"Successfully fetched balance",
            "Balance": balance
        }
        return jsonify(res),201
    else:
        res = {
            "msg":"Loading your balance failed",
            'wallet_related': wallet.public_key != None
        }
        return jsonify(res),500

@app.route('/broadcast-transaction',methods=['POST'])
def broadcast_tx():
    data = request.get_json()
    if not data:
        return jsonify({'msg':"Please enter transaction values"}),400
    
    required_field = ['sender','recipient','amount','signature']

    

    if not all(field in data for field in required_field):
        return jsonify({"message":"Please enter valid and complete values"}), 400
    
    success = blockchain.add_transaction(data['recipient'],data['sender'],data['signature'],data['amount'],is_receiving=True)
    if success:
        res = {
            "msg": "Succesfully added transaction wait for it to be mined",
            "transaction":{
                "sender":data['sender'],
                "recipient":data['recipient'],
                "signature":data['signature'],
                "amount": data['amount']
            }
            
            

        }
        return jsonify(res),201

    else:
        return jsonify({"msg":"Transaction Failed"}) , 500


@app.route('/broadcast-block',methods=['POST'])        
def broadcast_block():
    data = request.get_json()
    
    if not data:
        
        return jsonify({'msg':"Please enter transaction values"}),300
    
    
    
    if not 'block' in data:        
        return jsonify({'msg':"Please enter a block to broadcast"}),500
    

    block = data['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            print("the blockchain failed here on broadcasting")
            return jsonify({"msg":"broadcasted succesfully"}),201
        else:
            return jsonify({"msg":"Error in broadcasting"}),409

    elif block['index'] > blockchain.chain[-1].index:
        blockchain.resolve_conflicts = True
        return jsonify({"msg":"Blockchain is different from our local blockchain"}),200
        
    
    else:
        return jsonify({"msg":"Your blockchain is shorter"}),409



    

    

@app.route('/transactions',methods=['POST'])
def add_tx():
    if not wallet.public_key:
        return jsonify({"msg":"No Wallet was found"}), 400

    data = request.get_json()
    if not data:
        return jsonify({'msg':"Please enter transaction values"}),400
    
    required_field = ['recipient','amount']


    if not all(field in data for field in required_field):
        return jsonify({"message":"Please enter valid and complete values"}), 400
    
    recipient = data['recipient']
    amount = data['amount']

    signature = wallet.sign_tx(wallet.public_key,recipient,amount)
    if blockchain.add_transaction(recipient,wallet.public_key,signature,amount):
        res = {
            "msg": "Succesfully added transaction wait for it to be mined",
            "transaction":{
                "sender":wallet.public_key,
                "recipient":recipient,
                "signature":signature,
                "amount": amount
            }
            , 
            "balance": blockchain.get_balance()

        }
        return jsonify(res),201

    else:
        return jsonify({"msg":"Transaction Failed"}) , 500



@app.route('/transactions',methods=['GET'])

def get_open_tx():
    transactions = blockchain.get_open_tx()
    dict_tx = [tx.__dict__ for tx in transactions]
    res = {
        "msg":"Transactions fetched",
        "transactions": dict_tx
    }
    return jsonify(res),200



@app.route('/mine',methods=['POST'])
def mine():
    if blockchain.resolve_conflicts:
        return jsonify({"msg": "Block not added, Resolve conflicts first"})
    block = blockchain.mine_block()
    if block:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        res = {
            "msg":"Block Added Succesfully",
            "block": dict_block,
            "Balance": blockchain.get_balance()
        }
        return jsonify(res) , 201

       
    else:
        res = {
            'message':"Mining a block failed",
            'wallet_related': wallet.public_key != None
        }
        return jsonify(res),500


@app.route('/chain')
def get_chain():
    chain_data = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_data]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain),200


@app.route('/node',methods=['POST'])
def add_node():
    data = request.get_json()
    if not data:
        return jsonify({'msg':"Please enter transaction values"}),400

    if 'node' not in data:
        return jsonify({'msg':"Please enter a valid value"}),400

    node = data.get('node')
    blockchain.add_node(node)
    res = {
        "msg": "Node added succesfully",
        "all_nodes": blockchain.get_nodes()
    }
    return jsonify(res),201


@app.route('/node/<url>',methods=['DELETE'])

def remove_node(url):
    if url == '' or url == None:
        res = {
            'msg': 'That node is not found'
        }
        return jsonify(res),400
    blockchain.remove_node(url)
    res = {
        'msg': "Node removed succesfully",
        'all_nodes': blockchain.get_nodes()
    }
    return jsonify(res),201

@app.route('/nodes')

def get_nodes():
    return jsonify({
        "msg": "All nodes",
        "all_nodes": blockchain.get_nodes()
    }),200
    

@app.route('/resolve',methods=['POST'])

def resolve_conflict():
    replaced = blockchain.resolve_conflict()
    print(replaced)
    if replaced:
        return jsonify({"msg":"our chain was changed"}),200
    else:
        return jsonify({"msg":"Our chain is kept"}),200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p','--port',type=int,default=4000)
    args =  parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key,port)
    app.run(host='0.0.0.0',port=port)