import json

from utxo_manager import UTXOManager
from transactions import Transaction
from transactions import TransactionInput
from transactions import TransactionOutput
from transactions import CoinbaseTransaction
from key_manager import KeyManager


def main():

    k_m = KeyManager()
    um = UTXOManager(k_m.my_address())

    i_k_m = KeyManager()
    u_k_m = KeyManager()

    t1 = CoinbaseTransaction(k_m.my_address())
    t2 = CoinbaseTransaction(k_m.my_address())
    t3 = CoinbaseTransaction(k_m.my_address())

    t4 = Transaction(
      	[TransactionInput(t1.to_dict(), 0)],
      	[TransactionOutput(u_k_m.my_address(), 10.0), TransactionOutput(i_k_m.my_address(), 20.0)]
  	)


    transactions = []
    transactions.append(t1.to_dict())
    transactions.append(t2.to_dict())
    transactions.append(t3.to_dict())
    transactions.append(t4.to_dict())

    um.extract_utxos(transactions)

    balance = um.my_balance

    print(balance)


if __name__ == '__main__':
    main()