import threading
import time
from time import sleep

from blockchain.blockchain_manager import BlockchainManager
from blockchain.block_builder import BlockBuilder
from transaction.transaction_pool import TransactionPool


# TransactionPoolの確認頻度
CHECK_INTERVAL = 10
block_timer = None

def generate_block_with_tp(tp, bb, bm, prev_block_hash):

    result = tp.get_stored_transactions()
    if result != None:
        new_block = bb.generate_new_block(result, prev_block_hash)
        bm.set_new_block(new_block.to_dict())
        prev_block_hash = bm.get_hash(new_block.to_dict())
        # ブロック生成に成功したらTransaction Poolはクリアする
        index = len(result)
        tp.clear_my_transactions(index)
    else:
        print('Transaction Pool is empty ...') 

    print('Current Blockchain is ... ', bm.chain)
    print('Current prev_block_hash is ... ', prev_block_hash)

    block_timer = threading.Timer(CHECK_INTERVAL, generate_block_with_tp, args=(tp, bb, bm, prev_block_hash))
    block_timer.start()

def main():

    bb = BlockBuilder()
    my_genesis_block = bb.generate_genesis_block()
    bm = BlockchainManager(my_genesis_block.to_dict())
    
    tp = TransactionPool()

    prev_block_hash = bm.get_hash(my_genesis_block.to_dict())
    print('genesis_block_hash :' , prev_block_hash)
	
    transaction = { 
        'sender': 'test1',
        'recipient': 'test2',
        'value' : 3
    }
    
    tp.set_new_transaction(transaction)

    transaction2 = { 
        'sender': 'test1',
        'recipient': 'test3',
        'value' : 2
    }
    
    tp.set_new_transaction(transaction2)
    
    block_timer = threading.Timer(CHECK_INTERVAL, generate_block_with_tp, args=(tp, bb, bm, prev_block_hash))
    block_timer.start()

    sleep(15)
    
    transaction3 = { 
        'sender': 'test5',
        'recipient': 'test6',
        'value' : 10
    }
    
    tp.set_new_transaction(transaction3)


if __name__ == '__main__':
    main()