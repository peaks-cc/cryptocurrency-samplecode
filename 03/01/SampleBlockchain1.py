from blockchain.blockchain_manager import BlockchainManager
from blockchain.block_builder import BlockBuilder


def main():
    bb = BlockBuilder()
    my_genesis_block = bb.generate_genesis_block()
    bm = BlockchainManager(my_genesis_block.to_dict())

    prev_block_hash = bm.get_hash(my_genesis_block.to_dict())
    print('genesis_block_hash :' , prev_block_hash)
	
    transaction = { 
        'sender': 'test1',
        'recipient': 'test2',
        'value' : 3
    }
    
    new_block = bb.generate_new_block(transaction, prev_block_hash)
    bm.set_new_block(new_block.to_dict())
    
    new_block_hash = bm.get_hash(new_block.to_dict())
    print('1st_block_hash :' , new_block_hash)

    transaction2 = { 
        'sender': 'test1',
        'recipient': 'test3',
        'value' : 2
    }
    new_block2 = bb.generate_new_block(transaction2, new_block_hash) 
    bm.set_new_block(new_block2.to_dict())
    
    print(bm.chain)
    chain = bm.chain
    print(bm.is_valid(chain))

if __name__ == '__main__':
    main()