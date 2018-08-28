import threading

class TransactionPool:

    def __init__(self):
        print('Initializing TransactionPool...')
        self.transactions = []
        self.lock = threading.Lock()

    def set_new_transaction(self, transaction):
        with self.lock:
            print('set_new_transaction is called', transaction)
            self.transactions.append(transaction)

    def clear_my_transactions(self):
        with self.lock:
            self.transactions = []

    def get_stored_transactions(self):
        if len(self.transactions) > 0:
            return self.transactions
        else:
            print("Currently, it seems transaction pool is empty...")
            return None
