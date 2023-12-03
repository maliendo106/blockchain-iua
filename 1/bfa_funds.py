#!/usr/bin/env python3

import argparse
from sys import exit, stderr
from web3.middleware import geth_poa_middleware
from web3 import Web3
w3 = Web3

DEFAULT_WEB3_URI = "~/blockchain-iua/devnet/node/geth.ipc"

def connect_to_node(uri):
    if (uri.startswith("http://")):
        w3 = Web3(Web3.HTTPProvider(uri))
    else:
        w3 = Web3(Web3.IPCProvider(uri))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    if w3.is_connected():
        return w3
    else:
        print("Falla al contactar el nodo", file=stderr)
        exit(1) 

def balance(account, unit):
    """Imprime el balance de una cuenta

    :param account: La dirección de la cuenta
    :param unit: Las unidades en las que se desea el resultado. (wei, Kwei, Mwei, Gwei, microether, milliether, ether)
    """
    balance_wei = w3.eth.get_balance(account)
    balance = w3.from_wei(balance_wei, str(unit))
    print(f"balance: {balance} {unit}")

def transfer(src, dst, amount, unit):
    """Transfiere ether de una cuenta a otra.

    :param src: La dirección de la cuenta de origen.
    :param dst: La dirección de la cuenta de destino.
    :param amount: Monto que se desea transferir.
    :param unit: Unidades en las que está expresado el monto.
    Si la transacción es exitosa, imprime "Transferencia exitosa".
    Si la transacción falla, termina el programa con error e indica la causa.
    """
    amount_wei = w3.to_wei(amount, unit)
    txn = {
        'from': src,
        'to': dst,
        'value': amount_wei
    }

    # Enviar la transacción
    try:
        txn_hash = w3.eth.send_transaction(txn)
        print(f'Transferencia exitosa. Hash: {txn_hash.hex()}')
    except Exception as e:
        print(f'Error al enviar la transacción: {e}')
        exit(1)

def accounts():
    """Lista las cuentas asociadas con un nodo"""
    cuentas = w3.eth.accounts
    print(f"accounts(): {cuentas}")

def address(x):
    """Verifica si su argumento tiene forma de dirección ethereum válida"""
    
    if x[:2] == '0x' or x[:2] == '0X':
        try:
            b = bytes.fromhex(x[2:])
            if len(b) == 20:
                return x
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(f"Invalid address: '{x}'")                                                                                                                                               



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        f"""Maneja los fondos de una cuenta en una red ethereum.
        Permite consultar el balance y realizar transferencias. Por defecto, intenta conectarse mediante '{DEFAULT_WEB3_URI}'""")
    parser.add_argument("--uri", help=f"URI para la conexión con geth",default=DEFAULT_WEB3_URI)
    subparsers = parser.add_subparsers(title="command", dest="command")
    subparsers.required=True
    parser_balance = subparsers.add_parser("balance", help="Obtiene el balance de una cuenta")
    parser_balance.add_argument("--unit", help="Unidades en las que está expresado el monto", choices=['wei', 'Kwei', 'Mwei', 'Gwei', 'microether', 'milliether','ether'], default='wei')
    parser_balance.add_argument("--account", "-a", help="Cuenta de la que se quiere obtener el balance", type=address, required=True)
    parser_transfer = subparsers.add_parser("transfer", help="Transfiere fondos de una cuenta a otra")
    parser_transfer.add_argument("--from", help="Cuenta de origen", type=address, required=True, dest='src')
    parser_transfer.add_argument("--to", help="Cuenta de destino", type=address, required=True, dest='dst')
    parser_transfer.add_argument("--amount", help="Monto a transferir", type=int, required=True)
    parser_transfer.add_argument("--unit", help="Unidades en las que está expresado el monto", choices=['wei', 'Kwei', 'Mwei', 'Gwei', 'microether', 'milliether','ether'], default='wei')
    parser_accounts = subparsers.add_parser("accounts", help="Lista las cuentas de un nodo")
    args = parser.parse_args()
    # La URI elegida por el usuario está disponible como args.uri
    # Lo que sigue probablemente debería estar encerrado en un bloque try: ... except:

    try:
        w3 = connect_to_node(args.uri)

        if args.command == "balance":
            balance(args.account, args.unit)
        elif args.command == "transfer":
            transfer(args.src, args.dst, args.amount, args.unit)
        elif args.command == "accounts":
            accounts()
        else:
            print(f"Comando desconocido: {args.command}", file=stderr)
            exit(1)
    
    except ConnectionError as ce:
        print(f"Error de conexión: {ce}", file=stderr)
        exit(1)

    except ValueError as ve:
        print(f"Error de valor: {ve}", file=stderr)
        exit(1)

    except ModuleNotFoundError as me:
        print(f"Modulo faltante, instale con archio requeriments.txt", file=stderr)
        exit(1)

    except Exception as e:
        print(f"Ocurrió un error: {e}", file=stderr)
        exit(1)


"""
# recordar que la cuenta debe estar unlock
python3 bfa_funds.py --uri ~/bc/devnet/node/geth.ipc accounts
python3 bfa_funds.py --uri ~/bc/devnet/node/geth.ipc balance -a 0xe5f621F9c328BB2A05556d0d33AA94D172f3174C --unit ether
python3 bfa_funds.py --uri ~/bc/devnet/node/geth.ipc balance -a 0x79485Ef5627167779eaB2343f559cd7E2B5daF91 --unit ether
python3 bfa_funds.py --uri ~/bc/devnet/node/geth.ipc transfer --from 0xe5f621F9c328BB2A05556d0d33AA94D172f3174C --to 0x79485Ef5627167779eaB2343f559cd7E2B5daF91 --amount 1

"""