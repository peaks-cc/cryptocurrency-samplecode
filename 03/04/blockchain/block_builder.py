from .block import GenesisBlock
from .block import Block

class BlockBuilder:

    def __init__(self):
    	print('Initializing BlockBuilder...')
    	pass

    def generate_genesis_block(self):
    	genesis_block = GenesisBlock()
    	return genesis_block

    def generate_new_block(self, transaction, previous_block_hash):
        new_block = Block(transaction, previous_block_hash)
        return new_block


