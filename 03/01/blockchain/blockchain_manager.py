import json
import hashlib
import binascii
import threading

class BlockchainManager:

    def __init__(self, genesis_block):
        print('Initializing BlockchainManager...')    
        self.chain = []
        self.lock = threading.Lock()
        self.__set_my_genesis_block(genesis_block)

    def __set_my_genesis_block(self, block):
        self.genesis_block = block
        self.chain.append(block)

    def set_new_block(self, block):
        with self.lock:
            self.chain.append(block)

    def is_valid(self, chain):

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = self.chain[current_index]
            if block['previous_block'] != self.get_hash(last_block):
                return False		
                
            last_block = block
            current_index += 1

        return True

    def _get_double_sha256(self, message):
    	return hashlib.sha256(hashlib.sha256(message).digest()).digest()

    def get_hash(self, block):
        """
        正当性確認に使うためブロックのハッシュ値を取る
        :param block: Block
        """
        block_string = json.dumps(block, sort_keys=True)
        return binascii.hexlify(self._get_double_sha256((block_string).encode('utf-8'))).decode('ascii')
