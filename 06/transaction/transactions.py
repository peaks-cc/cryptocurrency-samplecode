from time import time

class TransactionInput:
    """
    トトランザクションの中でInputに格納するUTXOを指定する
    """
    def __init__(self, transaction, output_index):
        self.transaction = transaction
        self.output_index = output_index

    def to_dict(self):
        d = {
            'transaction': self.transaction,
            'output_index': self.output_index
        }
        return d

class TransactionOutput:
    """
    トランザクションの中で Output （送金相手と送る金額）を管理する
    """
    def __init__(self, recipient_address, value):
        self.recipient = recipient_address
        self.value = value

    def to_dict(self):
        d = {
            'recipient': self.recipient,
            'value': self.value
        }
        return d
    
class Transaction:
    """
    持っていないコインを誰かに簡単に送金できてしまっては全く意味がないので、過去のトランザクションにて
    自分を宛先として送金されたコインの総計を超える送金依頼を作ることができないよう、inputs と outputs
    のペアによって管理する

    Args:
        t_type : トランザクションのタイプ。今後の拡張で種別の切り分けに使う
        extra : 拡張用途で利用可能な文字列。例えば送金の際にその理由となった記事のURLを格納したい場合などに使う
    """
    def __init__(self, inputs, outputs, extra=None):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = time()
        self.t_type = 'basic'
        self.extra = extra


    def to_dict(self):
        d = {
            'inputs': list(map(TransactionInput.to_dict, self.inputs)),
            'outputs': list(map(TransactionOutput.to_dict, self.outputs)),
            'timestamp': self.timestamp, 
            't_type': self.t_type,
            'extra': self.extra
        }

        return d

    def is_enough_inputs(self, fee):
        total_in = sum(i.transaction['outputs'][i.output_index]['value'] for i in self.inputs)
        total_out = sum(int(o.value) for o in self.outputs) + int(fee)
        delta = total_in  - total_out
        if delta >= 0:
            return True
        else:
            return False

    def compute_change(self, fee):
        total_in = sum(i.transaction['outputs'][i.output_index]['value'] for i in self.inputs)
        total_out = sum(int(o.value) for o in self.outputs) + int(fee)
        delta = total_in  - total_out
        return delta

    
class CoinbaseTransaction(Transaction):
    """
    Coinbaseトランザクションは例外的にInputが存在しない。
    """
    def __init__(self, recipient_address, value=30):
        self.inputs = []
        self.outputs = [TransactionOutput(recipient_address, value)]
        self.timestamp = time()
        self.t_type = 'coinbase_transaction'

    def to_dict(self):
        d = {
            'inputs': [],
            'outputs': list(map(TransactionOutput.to_dict, self.outputs)),
            'timestamp' : self.timestamp,
            't_type': self.t_type
        }

        return d


