#!/usr/bin/env python3
from flask import Flask, request, make_response, json, jsonify
import re
import io
import json
from os import urandom, listdir
import os
from sys import argv, stderr, exit
from web3 import Web3, IPCProvider
from web3.middleware import geth_poa_middleware
from getpass import getpass
app = Flask(__name__)

hash_pattern = re.compile(r"0x[0-9a-fA-F]{64}")
blockNumber = 1

def is_valid_hash(h):
    return re.match(hash_pattern, h)

def get_private_key_from_file(filename):
    try:
        with open(filename) as f:
            encrypted_key = f.read()
        return w3.eth.account.decrypt(encrypted_key, getpass(prompt="Password: "))
    except ValueError:
        print("Contraseña incorrecta", file=stderr)
        exit(1)
    except FileNotFoundError as e:
        print(e, file = stderr)
        exit(1)

from eth_account.messages import encode_defunct
from eth_account import Account

def is_valid_signature(hash_value, signature):
    message = encode_defunct(hexstr=hash_value) # el mensaje que es el hash encodeado
    #print(signature)
    #signature_bytes = bytes.fromhex(signature[2:])
    #v_bytes = signature_bytes[-2:]
    #v = int.from_bytes(v_bytes, byteorder='little')
    #print(v)
    signature_ = signature[2:]

    try:
        signing_address = Account.recover_message(message, signature=signature_) #vrs=(v, r, s)
        #print(f"==============signing_address'{str(signing_address).lower()}'")
        return True
    except Exception:
        return False
     

@app.get("/stamped/<hash_value>")
def stamped(hash_value):
    response = None

    if is_valid_hash(hash_value):
        s = contract.functions.stamped(hash_value).call()
        if s:
            if(s[1] != 0): # blockNumber != 0
                j={'signer':str(s[0]),'blockNumber':s[1]}
                response = jsonify(j)
                response.status_code = 200
                response.headers["Content-Type"] = "application/json; charset=utf-8"
            else:
                response = jsonify(message="Hash not found")
                response.status_code = 404
        else:
            response = jsonify(message="Hash not found")
            response.status_code = 404
    else:
        response = jsonify(message="Invalid hash format")
        response.status_code = 400

    return response


@app.post("/stamp")
def stamp():
    global blockNumber
    response = None

    if request.mimetype != "application/json":
        response = jsonify(message=f"Invalid message mimetype: '{request.mimetype}'")
        response.status_code = 400
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        
    req = request.json
    hash_value = req.get("hash")

    if is_valid_hash(hash_value) is False:
        response = jsonify(message="Invalid hash format")
        response.status_code = 400 # Bad Request
        response.headers["Content-Type"] = "application/json; charset=utf-8"

    s = contract.functions.stamped(hash_value).call()   #Me fijo si ese hash fue stamped

    if(s[1] != 0): #Ese hash ya esta siendo usado por alguien 
        j={'message': "Forbidden",'signer':str(s[0]),'blockNumber':s[1]}
        response = jsonify(j)
        response.status_code = 403
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response 

    signature = req.get("signature")
    account = w3.eth.account.from_key(private_key).address  #Registro cuenta

    if signature is not None:
        if is_valid_signature(hash_value, signature) is False:#signature no valido
            j={'message': "Bad Request"}
            response = jsonify(j)   
            response.status_code = 400
            response.headers["Content-type"] = "application/json; charset=utf-8"
            return response

    if signature is not None:  #stamSigned() 
        s = contract.functions.stampSigned(hash_value, signature).build_transaction({'gas': 100000,'gasPrice': w3.eth.gas_price,'nonce': w3.eth.get_transaction_count(account)})
    else: #stamp()
        s = contract.functions.stamp(hash_value).build_transaction({'gas': 100000,'gasPrice': w3.eth.gas_price,'nonce': w3.eth.get_transaction_count(account)})
   
    signed_transaction = w3.eth.account.sign_transaction(s, private_key = private_key)
    txh = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txh)

    if receipt.status == 1: # no fracaso
        j={'transaction':str(txh.hex()),'blockNumber':receipt.get("blockNumber")}
        response = jsonify(j)
        response.status_code = 201
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    else:# fracaso
        response = jsonify({"message": "The hash is already stamped", "blockNumber": receipt.get("blockNumber"), "signer": receipt.get("signer")})
        response.status_code = 403
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response


if __name__ == '__main__':
    import argparse
    
    ipc_path = os.path.expanduser("~/blockchain-iua/bfatest/node/geth.ipc")
    file_path = "../../Stamper.json"
    keystore_dir = os.path.expanduser("~/blockchain-iua/bfatest/node/keystore")

    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", "-u", help=f"URI para la conexión con geth",default=ipc_path)
    parser.add_argument("--stamper", "-s", help=f"URI del archivo Stamper.json",default=file_path)
    parser.add_argument("--keystore", "-k", help=f"URI del directorio keystore",default=keystore_dir)
    args = parser.parse_args()

    if(args.uri is not None):
        ipc_path = args.uri
    if(args.stamper is not None):
        file_path = args.stamper
    if(args.keystore is not None):
        keystore_dir = args.keystore

    try:
        w3 = Web3(IPCProvider(ipc_path))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    except:
        print("Ocurrió un error conectandose con el archivo geth.ipc")

    with open(file_path) as f:
        config = json.load(f)
        contract = w3.eth.contract(abi = config['abi'], address = config["networks"]["55555000000"]["address"])

    keystore = list(map(lambda f: os.path.join(
        keystore_dir, f), sorted(listdir(keystore_dir))))
    with open(keystore[0]) as f:
        sender = f"0x{json.load(f)['address']}"
    sender = w3.to_checksum_address(sender)
    
    try:
        private_key = get_private_key_from_file(keystore[0])
    except FileNotFoundError:
        print("No se pudo encontrar el archivo")
        exit(1)
        
    app.run(debug=True)
