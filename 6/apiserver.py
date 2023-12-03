#!/usr/bin/env python3
from flask import Flask, request, make_response, json, jsonify
from flask_cors import CORS
import re
import json
from os import urandom
import sys 
from web3 import Web3
from web3.middleware import geth_poa_middleware
from getpass import getpass
import messages
import argparse
from eth_account.messages import encode_defunct, SignableMessage
from eth_account import Account
from dateutil.parser import parse
from eth_utils import to_bytes, decode_hex, is_checksum_address
import pytz
from datetime import datetime
from dateutil.parser import isoparse
app = Flask(__name__)
CORS(app)

ACCOUNT_PATH = "m/44'/60'/0'/0/0"
hash_pattern = re.compile(r"0x[0-9a-fA-F]{64}")

def is_valid_hash(h):
    return re.match(hash_pattern, h)

def responses(body, code):
    response = jsonify(body)
    response.status_code = code
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

def is_valid_callId(hex_str):
    if len(hex_str) != 66: # longitud de 66 caracteres
        return False
    if not hex_str.startswith("0x"):
        return False
    hex_str = hex_str[2:] # quita los primeros dos caracteres "0x"
    try:
        int(hex_str, 16) # intenta convertir la cadena a un entero hexadecimal
    except ValueError:
        return False
    return True

def sign(message: str, account: Account) -> str:
    """Firma un mensaje desde la cuenta especificada."""
    signable_message: SignableMessage = encode_defunct(hexstr=message)
    return account.sign_message(signable_message).signature.hex()

@app.post("/create")
def create():
    content_type = request.headers.get('Content-Type', '')
    if 'application/json' not in content_type:
        j={'message': messages.INVALID_MIMETYPE}
        return responses(j, 400)
    
    req = request.get_json()
    call_id = req.get("callId")
    if is_valid_callId(call_id) is False:
        j={'message': messages.INVALID_CALLID}
        return responses(j, 400)      

    closing_time = req.get("closingTime") # "2023-06-15T18:30:00Z" formato ISO 8601
    try:
        parse(closing_time)
    except ValueError:
        j={'message': messages.INVALID_TIME_FORMAT}
        return responses(j, 400) 

    current_time = datetime.now().isoformat()
    if closing_time < current_time: #no puede estar en el pasado
        j={'message': messages.INVALID_CLOSING_TIME}
        return responses(j, 400)        

    dt = datetime.fromisoformat(closing_time)
    timestamp = int(dt.timestamp())
    closing_time = timestamp * (10 ** 18)

    signature = req.get("signature") #firma(direccion_contrato(bytes) + callId(bytes))       
    if re.match("^0x[0-9a-fA-F]{64}$", signature) is False:
        j={'message': messages.INVALID_SIGNATURE}
        return responses(j, 400)
    signature_ = signature
    if signature.startswith("0x"):
        signature_ = bytes.fromhex(signature[2:])

    contract_address_bytes = to_bytes(hexstr=address_contract)
    call_id_bytes = decode_hex(call_id)
    message = encode_defunct(contract_address_bytes + call_id_bytes)
    creator = None
    try:
        creator = Account.recover_message(message, signature=signature_)
    except:
        j={'message': messages.INVALID_SIGNATURE}
        return responses(j, 400)       

    try:
        contract.functions.createFor(call_id, closing_time, creator).transact()
        j={'message': messages.OK}
        return responses(j, 201)
    except Exception as e:
        if 'El llamado ya existe' in str(e):
            j={'message': messages.ALREADY_CREATED}
            return responses(j, 403) 
        elif 'No autorizado' in str(e):
            j={'message': messages.UNAUTHORIZED}
            return responses(j, 403) 
        elif 'Solo el creador puede hacer esta llamada' in str(e):
            j={'message': messages.UNAUTHORIZED}
            return responses(j, 403)         
        else:
            j={'message': messages.INTERNAL_ERROR}
            return responses(j, 500) 

@app.post("/register")
def register(): 
    content_type = request.headers.get('Content-Type', '')
    if 'application/json' not in content_type:
        j={'message': messages.INVALID_MIMETYPE}
        return responses(j, 400)
    
    req = request.get_json()
    addr = req.get("address")
    if is_checksum_address(addr) is False:
        j={'message': messages.INVALID_ADDRESS}
        return responses(j, 400) 
    
    signature = req.get("signature")      
    if re.match("^0x[0-9a-fA-F]{64}$", signature) is False:
        j={'message': messages.INVALID_SIGNATURE}
        return responses(j, 400)
    signature_ = signature
    if signature.startswith("0x"):
        signature_ = bytes.fromhex(signature[2:])
    contract_address_bytes = to_bytes(hexstr=address_contract)
    message = encode_defunct(contract_address_bytes)  
    try:
        singing_addr = Account.recover_message(message, signature=signature_)
        #print(f"========address original====={addr}")
        #print(f"========signing  address====={singing_addr}")
    except:
        j={'message': messages.INVALID_SIGNATURE}
        return responses(j, 400) 
    if addr != singing_addr:
        j={'message': messages.INVALID_SIGNATURE}
        return responses(j, 400) 

    try:
        if contract.functions.isRegistered(addr).call():
            j={'message': messages.ALREADY_AUTHORIZED}
            return responses(j, 403)    
        tx_hash = contract.functions.authorize(addr).transact()
        j={'message': messages.OK}
        return responses(j, 200)
    except Exception as e:
        if 'Ya se ha registrado' in str(e):
            j={'message': messages.ALREADY_AUTHORIZED}
            return responses(j, 403)
        else:
            j={'message': messages.INTERNAL_ERROR}
            return responses(j, 500)

@app.post("/register-proposal")
def register_proposal():
    content_type = request.headers.get('Content-Type', '')
    if 'application/json' not in content_type:
        j={'message': messages.INVALID_MIMETYPE}
        return responses(j, 400)
    
    req = request.get_json()
    call_id = req.get("callId")
    if is_valid_callId(call_id) is False:
        j={'message': messages.INVALID_CALLID}
        return responses(j, 400) 

    proposal = req.get("proposal")
    if is_valid_callId(proposal) is False:
        j={'message': messages.INVALID_PROPOSAL}
        return responses(j, 400)
    try:
        contract.functions.registerProposal(call_id, proposal).transact()
        j={'message': messages.OK}
        return responses(j, 201)
    except Exception as e:
        if 'El llamado no existe' in str(e):
            j={'message': messages.CALLID_NOT_FOUND}
            return responses(j, 404)
        elif 'La propuesta ya ha sido registrada' in str(e):
            j={'message': messages.ALREADY_REGISTERED}
            return responses(j, 403)
        else:
            j={'message': messages.INTERNAL_ERROR}
            return responses(j, 500)

@app.get("/authorized/<address_value>")
def authorized(address_value):
    if bool(re.match(r"^0x[0-9a-fA-F]{40}$", address_value)) is False:
        j={'message': messages.INVALID_ADDRESS}
        return responses(j, 400) 
    try:
        autorizado = contract.functions.isAuthorized(address_value).call()
        j={'authorized': autorizado}
        return responses(j, 200)
    except:
        j={'authorized': False}
        return responses(j, 200)      

@app.get("/calls/<call_id>")
def calls(call_id):
    if is_valid_callId(call_id) is False:
        j={'message': messages.INVALID_CALLID}
        return responses(j, 400) 
    
    try:
        call_for_proposals = contract.functions.calls(call_id).call()
        creator = call_for_proposals[0]
        if creator == '0x0000000000000000000000000000000000000000':
            j={'message': messages.CALLID_NOT_FOUND} #no hay call_for_proposals para ese callId
            return responses(j, 404)
        cfp = call_for_proposals[1]
        j={'creator': creator, 'cfp': cfp}
        return responses(j, 200)
    except:
        j={'message': messages.INTERNAL_ERROR}
        return responses(j, 500)

@app.get("/closing-time/<call_id>")
def closing_time(call_id):
    if is_valid_callId(call_id) is False:
        j={'message': messages.INVALID_CALLID}
        return responses(j, 400) 

    try:
        call_for_proposals = contract.functions.calls(call_id).call()
        creator = call_for_proposals[0]
        if creator == '0x0000000000000000000000000000000000000000':
            j={'message': messages.CALLID_NOT_FOUND}
            return responses(j, 404)
        cfp = call_for_proposals[1]
        # Crea una instancia del contrato CFP utilizando la dirección
        cfp_contract = web3.eth.contract(address=cfp, abi=cfp_abi)
        closing_time = cfp_contract.functions.closingTime().call()
        timestamp = closing_time // (10 ** 18) #timestamp en segundos
        dt = datetime.fromtimestamp(timestamp, tz=pytz.timezone('Etc/GMT-3'))
        iso_string = dt.isoformat()
        j={'closingTime': iso_string}
        return responses(j, 200)
    except:
        j={'message': messages.INTERNAL_ERROR}
        return responses(j, 500)

@app.get("/contract-address")
def contract_address():
    j={'address': (contract.address)}
    return responses(j, 200)

@app.get("/contract-owner")
def contract_owner():
    j={'address': contract.functions.owner().call()}
    return responses(j, 200)

@app.get("/proposal-data/<call_id>/<proposal>")
def proposal_data(call_id, proposal):
    if is_valid_callId(call_id) is False:
        j={'message': messages.INVALID_CALLID}
        return responses(j, 400) 

    if is_valid_callId(proposal) is False:
        j={'message': messages.INVALID_PROPOSAL}
        return responses(j, 400)

    cfp = None
    try:
        call_for_proposals = contract.functions.calls(call_id).call()
        cfp = call_for_proposals[1]
        if call_for_proposals[0] == '0x0000000000000000000000000000000000000000':
            j={'message': messages.CALLID_NOT_FOUND}
            return responses(j, 404)
    
        # Crea una instancia del contrato CFP utilizando la dirección
        cfp_contract = web3.eth.contract(address=cfp, abi=cfp_abi)
        proposal_data = cfp_contract.functions.proposalData(proposal).call()
        sender = proposal_data[0]
        if sender == '0x0000000000000000000000000000000000000000':
            j={'message': messages.PROPOSAL_NOT_FOUND}
            return responses(j, 404)
        block_number = proposal_data[1]
        timestamp = proposal_data[2]
        timestamp = timestamp // (10 ** 9) #timestamp en segundos
        dt = datetime.fromtimestamp(timestamp, tz=pytz.timezone('Etc/GMT-3'))
        iso_string = dt.isoformat()
        j={'sender': sender, 'blockNumber': int(block_number), 'timestamp': iso_string}
        return responses(j, 200)
    except:
        j={'message': messages.INTERNAL_ERROR}
        return responses(j, 500)



# ============ util endpoints ====================
@app.get("/utils/random/hex")
def random_hex():
    hexa = f"0x{urandom(32).hex()}"
    j={'random_hex': hexa}
    return responses(j, 200)

@app.get("/utils/signature")
def utils_signature_addr():
    contract_address = contract.address
    account = Account().create()
    signature_register = sign(contract_address, account)

    signature = []
    call_id = [f"0x{urandom(32).hex()}" for _ in range(3)]

    for aux in call_id:
        message_bytes = bytes.fromhex(contract_address[2:]) + bytes.fromhex(aux[2:])
        signature.append(sign(message_bytes.hex(), account))

    j={'address': account.address, 
    'signature_register': signature_register,
    'call_id': call_id,
    'signature_create': signature}
    return responses(j, 200)

@app.get("/calls")
def util_calls_nuevo():
    creators = []
    creator_length = contract.functions.creatorsCount().call()
    for i in range(creator_length):
        creators.append(contract.functions.creatorsList(i).call())
    
    call = []
    for addr in creators:
        # cantidad de llamados creados por addr
        call_length = contract.functions.createdByCount(addr).call()
        for i in range(call_length):
            call.append(contract.functions.createdBy(addr, i).call().hex())

    j={'calls': call}
    return responses(j, 200)

@app.get("/register/list")
def util_register_list():
    """lista las registraciones en estado PENDIENTE"""
    register_list = contract.functions.getAllPending().call()

    j={'registers': register_list}
    return responses(j, 200)

@app.post("/utils/register/account")
def util_register():
    """registra una cuenta, pero queda en estado 
    PENDIENTE hasta que el duenio lo autorize"""
    req = request.get_json()
    addr = req.get("account")
    try:
        contract.functions.register().transact({'from': addr})
    except Exception as e:
        j={'message': messages.INTERNAL_ERROR}
        return responses(j, 500)

    j={'message': messages.OK}
    return responses(j, 200)

@app.post("/register/auth")
def util_authorize():
    """quita una cuenta de la lista de PENDIENTES
    y la AUTORIZA a crear llamados"""
    req = request.get_json()
    addr = req.get("account")
    try:    
        tx_hash = contract.functions.authorize(addr).transact()
        j={'message': messages.OK}
        return responses(j, 200)
    except Exception as e:
        if 'Ya se ha registrado' in str(e):
            j={'message': messages.ALREADY_AUTHORIZED}
            return responses(j, 403)
        else:
            j={'message': messages.INTERNAL_ERROR}
            return responses(j, 500)
#==========================================================

if __name__ == '__main__':
    import argparse
    
    ganache_url = "http://localhost:7545"
    mnemonic_path = None
    abi_path = "../5/build/contracts/CFPFactory.json"
    abi_cfp = "../5/build/contracts/CFP.json"

    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", "-u", help=f"URI para la conexión con Ganache",default=ganache_url)
    parser.add_argument("--mnemonic", "-m", help=f"URI del archivo Mnemonic",default=mnemonic_path)
    args = parser.parse_args()

    if(args.mnemonic is None):
        mnemonic = input("Mnemonic: ")
    else:
        mnemonic_path = args.mnemonic
        with open(mnemonic_path) as f: # Leer la mnemónica del archivo
            mnemonic = f.read().strip() 
    if(args.uri is not None):
        ganache_url = args.uri

    address_contract = None
    contract = None
    cfp_abi = None
    account = None
    try:
        ganache_provider = Web3.HTTPProvider(ganache_url)
        web3 = Web3(ganache_provider)

        # Establecer el proveedor de cuentas con la mnemónica especificada
        from web3.middleware import geth_poa_middleware
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        web3.eth.account.enable_unaudited_hdwallet_features()
        account = web3.eth.account.from_mnemonic(mnemonic, account_path=ACCOUNT_PATH) #account_path="m/44'/60'/0'/0/0"
        web3.eth.default_account = account.address

        with open(abi_path) as f:
            config = json.load(f)
            address_contract = config["networks"]["5777"]["address"]
            contract = web3.eth.contract(abi = config['abi'], address = address_contract)

        with open(abi_cfp) as f:
            config = json.load(f)
            cfp_abi = config['abi']

        print("Conectado a Ganache con dirección:", account.address)
    except:
        print("Ocurrió un error conectandose con Ganache")
 
    app.run(debug=True)


"""
========== utils ==========
truffle migrate --network ganache
python3 apiserver.py --mnemonic mnemonic
"""