import time
import socket, threading, json

from blockchain.blockchain_manager import BlockchainManager
from blockchain.block_builder import BlockBuilder
from transaction.transaction_pool import TransactionPool
from p2p.connection_manager import ConnectionManager
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
from p2p.message_manager import (
    MSG_NEW_TRANSACTION,
    MSG_NEW_BLOCK,
    MSG_REQUEST_FULL_CHAIN,
    RSP_FULL_CHAIN,
    MSG_ENHANCED,
)

STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3

# TransactionPoolの確認頻度
# 動作チェック用に数字小さくしてるけど、600(10分)くらいはあって良さそ
CHECK_INTERVAL = 10


class ServerCore(object):

    def __init__(self, my_port = 50082, core_node_host=None, core_node_port=None):
        self.server_state = STATE_INIT
        print('Initializing server...')
        self.my_ip = self.__get_myip()
        print('Server IP address is set to ... ', self.my_ip)
        self.my_port = my_port
        self.cm = ConnectionManager(self.my_ip, self.my_port, self.__handle_message)
        self.mpmh = MyProtocolMessageHandler()
        self.core_node_host = core_node_host
        self.core_node_port = core_node_port
        
        self.bb = BlockBuilder()
        my_genesis_block = self.bb.generate_genesis_block()
        self.bm = BlockchainManager(my_genesis_block.to_dict())
        self.prev_block_hash = self.bm.get_hash(my_genesis_block.to_dict())    
        self.tp = TransactionPool()

    def start(self):
        self.server_state = STATE_STANDBY
        self.cm.start()
        
        self.bb_timer = threading.Timer(CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()

    def join_network(self):
        if self.core_node_host != None:
            self.server_state = STATE_CONNECTED_TO_NETWORK # 状態：親ノードへ接続中
            self.cm.join_network(self.core_node_host, self.core_node_port)
        else:
            print('This server is runnning as Genesis Core Node...')

    def shutdown(self):
        self.server_state = STATE_SHUTTING_DOWN # 状態：切断中
        print('Shutdown server...')
        self.cm.connection_close()

    def get_my_current_state(self):
        return self.server_state
        
    def __generate_block_with_tp(self):

        result = self.tp.get_stored_transactions()
        print('generate_block_with_tp called!')
        if len(result) == 0:
            print('Transaction Pool is empty ...')
        new_block = self.bb.generate_new_block(result, self.prev_block_hash)
        self.bm.set_new_block(new_block.to_dict())
        self.prev_block_hash = self.bm.get_hash(new_block.to_dict())
        # ブロック生成に成功したらTransaction Poolはクリアする
        index = len(result)
        self.tp.clear_my_transactions(index)

        print('Current Blockchain is ... ', self.bm.chain)
        print('Current prev_block_hash is ... ', self.prev_block_hash)

        self.bb_timer = threading.Timer(CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()

    def __handle_message(self, msg, is_core, peer=None):
        if peer != None:
            if msg[2] == MSG_REQUEST_FULL_CHAIN:
                # TODO: 現状はMSG_REQUEST_FULL_CHAINの時くらいしか想定してないけどとりあえず
                print('Send our latest blockchain for reply to : ', peer)
                pass
        else:
            if msg[2] == MSG_NEW_TRANSACTION:
                # 新規transactionを登録する処理を呼び出す
                new_transaction = json.loads(msg[4])
                print("received new_transaction", new_transaction)
                current_transactions = self.tp.get_stored_transactions()
                has_same = False
                if new_transaction in current_transactions:
                    print("this is already pooled transaction:", t)
                    return

                if not is_core:
                    self.tp.set_new_transaction(new_transaction)
                    new_message = self.cm.get_message_text(MSG_NEW_TRANSACTION, json.dumps(new_transaction))
                    self.cm.send_msg_to_all_peer(new_message)
                else:
                    self.tp.set_new_transaction(new_transaction)

            elif msg[2] == MSG_NEW_BLOCK:
                # TODO: 新規ブロックを検証する処理を呼び出す
                pass
            elif msg[2] == RSP_FULL_CHAIN:
                # TODO: ブロックチェーン送信要求に応じて返却されたブロックチェーンを検証する処理を呼び出す
                pass
            elif msg[2] == MSG_ENHANCED:
                # P2P Network を単なるトランスポートして使っているアプリケーションが独自拡張したメッセージはここで処理する。SimpleBitcoin としてはこの種別は使わない
                self.mpmh.handle_message(msg[4])

    def __get_myip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]