import json
import hashlib
import binascii
import pickle
import copy
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

    def renew_my_blockchain(self, blockchain):
        # ブロックチェーン自体を更新し、それによって変更されるはずの最新のprev_block_hashを計算して返却する
        with self.lock:
            if self.is_valid_chain(blockchain):
                self.chain = blockchain
                latest_block = self.chain[-1]
                return self.get_hash(latest_block)
            else:
                print('invalid chain cannot be set...')
                return None

    def get_my_blockchain(self):
        if len(self.chain) > 1:
            return self.chain
        else:
            return None
            
    def get_my_chain_length(self):
        return len(self.chain)


    def get_transactions_from_orphan_blocks(self, orphan_blocks):
        current_index = 1
        new_transactions = []

        while current_index < len(orphan_blocks):
            block = orphan_blocks[current_index]
            transactions = block['transactions']
            target = self.remove_useless_transaction(transactions)
            for t in target:
                new_transactions.append(t)

        return new_transactions


    def remove_useless_transaction(self, transaction_pool):
        """
        与えられたTransactionのリストの中で既に自分が管理するブロックチェーン内に含まれたTransactionがある場合、それを削除したものを返却する
            param :
                transaction_pool: 検証したいTransactionのリスト。TransactionPoolに格納されているデータを想定

            return :
                整理されたTransactionのリスト。与えられたリストがNoneの場合にはNoneを返す
        """

        if len(transaction_pool) != 0:
            current_index = 1

            while current_index < len(self.chain):
                block = self.chain[current_index]
                transactions = block['transactions']
                for t in transactions:
                    for t2 in transaction_pool:
                        # ブロックに格納するタイミングで json.dumps してるので普通に比較すると死ぬ
                        if t == json.dumps(t2):
                            print('already exist in my blockchain :', t2)
                            transaction_pool.remove(t2)

                current_index += 1
            return transaction_pool
        else:
            print('no transaction to be removed...')
            return []

    def resolve_conflicts(self, chain):
        # 自分のブロックチェーンと比較して、長い方を有効とする。有効性検証自体はrenew_my_blockchainで実施
        mychain_len = len(self.chain)
        new_chain_len = len(chain)

        pool_4_orphan_blocks = copy.deepcopy(self.chain)
        has_orphan = False

        # 自分のチェーンの中でだけ処理済みとなっているTransactionを救出する。現在のチェーンに含まれていない
        # ブロックを全て取り出す。時系列を考えての有効無効判定などはしないかなり簡易な処理。
        if new_chain_len > mychain_len:
            for b in pool_4_orphan_blocks:
                for b2 in chain:
                    if b == b2:
                        pool_4_orphan_blocks.remove(b)

            result = self.renew_my_blockchain(chain)
            print(result)
            if result is not None:
                return result, pool_4_orphan_blocks
            else:
                return None, []
        else:
            print('invalid chain cannot be set...')
            return None, []

    def is_valid_block(self, prev_block_hash, block, difficulty=3):
        # ブロック単体の正当性を検証する
        suffix = '0' * difficulty
        block_4_pow = copy.deepcopy(block)
        nonce = block_4_pow['nonce']
        del block_4_pow['nonce']
        print(block_4_pow)

        message = json.dumps(block_4_pow, sort_keys=True)
        # print("message", message)
        nonce = str(nonce)

        if block['previous_block'] != prev_block_hash:
            print('Invalid block (bad previous_block)')
            print(block['previous_block'])
            print(prev_block_hash)
            return False
        else:
            digest = binascii.hexlify(self._get_double_sha256((message + nonce).encode('utf-8'))).decode('ascii')
            if digest.endswith(suffix):
                print('OK, this seems valid block')
                return True
            else:
                print('Invalid block (bad nonce)')
                print('nonce :' , nonce)
                print('digest :' , digest)
                print('suffix', suffix)
                return False

    def is_valid_chain(self, chain):
        # ブロック全体の正当性を検証する
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if self.is_valid_block(self.get_hash(last_block), block) is not True:
                return False		
                
            last_block = chain[current_index]
            current_index += 1

        return True


    def _get_double_sha256(self,message):
    	return hashlib.sha256(hashlib.sha256(message).digest()).digest()

    def get_hash(self,block):
        """
        正当性確認に使うためブロックのハッシュ値を取る
            param 
                block: Block
        """
        print('BlockchainManager: get_hash was called!')
        block_string = json.dumps(block, sort_keys=True)
        # print("BlockchainManager: block_string", block_string)
        return binascii.hexlify(self._get_double_sha256((block_string).encode('utf-8'))).decode('ascii')
