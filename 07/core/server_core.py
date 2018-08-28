import socket
import threading
import json
import pickle
import time
import copy

from blockchain.blockchain_manager import BlockchainManager
from blockchain.block_builder import BlockBuilder
from transaction.transaction_pool import TransactionPool
from transaction.utxo_manager import UTXOManager
from transaction.transactions import CoinbaseTransaction
from utils.key_manager import KeyManager
from utils.rsa_util import RSAUtil
from p2p.my_protocol_message_store import MessageStore
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
STATE_CONNECTED_TO_CENTRAL = 2
STATE_SHUTTING_DOWN = 3

# TransactionPoolの確認頻度
# 動作チェック用に数字小さくしてるけど、600(10分)くらいはあって良さそ
CHECK_INTERVAL = 10


class ServerCore:

    def __init__(self, my_port = 50082, core_node_host=None, core_node_port=None, pass_phrase=None):
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
        self.is_bb_running = False
        self.flag_stop_block_build = False
        self.mpm_store = MessageStore()
        self.km = KeyManager(None, pass_phrase)
        self.rsa_util = RSAUtil()
        self.um = UTXOManager(self.km.my_address())

    def start_block_building(self):
        self.bb_timer = threading.Timer(CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()

    def stop_block_building(self):
        print('Thread for __generate_block_with_tp is stopped now')
        self.bb_timer.cancel()

    def start(self):
        self.server_state = STATE_STANDBY
        self.cm.start()
        self.start_block_building()

    def join_network(self):
        if self.core_node_host != None:
            self.server_state = STATE_CONNECTED_TO_CENTRAL
            self.cm.join_network(self.core_node_host, self.core_node_port)
        else:
            print('This server is runnning as Genesis Core Node...')

    def shutdown(self):
        self.server_state = STATE_SHUTTING_DOWN
        self.flag_stop_block_build = True
        print('Shutdown server...')
        self.cm.connection_close()
        self.stop_block_building()

    def get_my_current_state(self):
        return self.server_state

    def send_req_full_chain_to_my_peer(self):
        print('send_req_full_chain_to_my_central called')
        new_message = self.cm.get_message_text(MSG_REQUEST_FULL_CHAIN)
        self.cm.send_msg((self.core_node_host, self.core_node_port),new_message)

    def get_all_chains_for_resolve_conflict(self):
        print('get_all_chains_for_resolve_conflict called')
        new_message = self.cm.get_message_text(MSG_REQUEST_FULL_CHAIN)
        self.cm.send_msg_to_all_peer(new_message)

    def __generate_block_with_tp(self):

        print('Thread for generate_block_with_tp started!')
        while not self.flag_stop_block_build:
            self.is_bb_running = True
            prev_hash = copy.copy(self.prev_block_hash)
            result = self.tp.get_stored_transactions()
            if len(result) == 0:
                print('Transaction Pool is empty ...')
                break
            new_tp = self.bm.remove_useless_transaction(result)
            self.tp.renew_my_transactions(new_tp)
            if len(new_tp) == 0:
                break
            # リワードとしてリストの先頭に自分宛のCoinbaseTransactionを追加する
            total_fee = self.tp.get_total_fee_from_tp()
            # TODO: インセンティブの値をここに直書きするのはイケてないのであとで対処する
            total_fee += 30
            my_coinbase_t = CoinbaseTransaction(self.km.my_address(), total_fee)
            transactions_4_block = copy.deepcopy(new_tp)
            transactions_4_block.insert(0, my_coinbase_t.to_dict())
            new_block = self.bb.generate_new_block(transactions_4_block, prev_hash)
            # タイミングがどうしてもクロスするので念のため保存前に再度確認
            if new_block.to_dict()['previous_block'] == self.prev_block_hash:
                self.bm.set_new_block(new_block.to_dict())
                self.prev_block_hash = self.bm.get_hash(new_block.to_dict())
                msg_new_block = self.cm.get_message_text(MSG_NEW_BLOCK, json.dumps(new_block.to_dict()))
                self.cm.send_msg_to_all_peer(msg_new_block)
                # ブロック生成に成功したらTransaction Poolはクリアする
                index = len(new_tp)
                self.tp.clear_my_transactions(index)
                break
            else:
                print('Bad block. It seems someone already win the PoW.')
                break

        print('Current Blockchain is ... ', self.bm.chain)
        print('Current prev_block_hash is ... ', self.prev_block_hash)
        self.flag_stop_block_build = False
        self.is_bb_running = False
        self.bb_timer = threading.Timer(CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()

    def _check_availability_of_transaction(self, transaction):
        """
        Transactionに含まれているTransactionInputの有効性（二重使用）を検証する
        """
        v_result, used_outputs = self.rsa_util.verify_sbc_transaction_sig(transaction)
        if v_result is not True:
            print('signature verification error on new transaction')
            return False

        for used_o in used_outputs:
            print('used_o', used_o)
            bm_v_result = self.bm.has_this_output_in_my_chain(used_o)
            tp_v_result = self.tp.has_this_output_in_my_tp(used_o)
            bm_v_result2 = self.bm.is_valid_output_in_my_chain(used_o)
            if bm_v_result:
                print('This TransactionOutput is already used', used_o)
                return False
            if tp_v_result:
                print('This TransactionOutput is already stored in the TransactionPool', used_o)
                return False
            if bm_v_result2 is not True:
                print('This TransactionOutput is unknown', used_o)
                return False

        return True

    def _check_availability_of_transaction_in_block(self, transaction):
        """
        Transactionの有効性を検証する（Block用）
        """
        v_result, used_outputs = self.rsa_util.verify_sbc_transaction_sig(transaction)
        if v_result is not True:
            print('signature verification error on new transaction')
            return False

        print('used_outputs: ', used_outputs)

        for used_o in used_outputs:
            print('used_o: ',used_o)
            bm_v_result = self.bm.has_this_output_in_my_chain(used_o)
            bm_v_result2 = self.bm.is_valid_output_in_my_chain(used_o)
            if bm_v_result2 is not True:
                print('This TransactionOutput is unknown', used_o)
                return False
            if bm_v_result:
                print('This TransactionOutput is already used', used_o)
                return False

        return True

    def get_total_fee_on_block(self, block):
        """
        ブロックに格納されているbasicなTransaction全ての手数料の合計値を算出する
        """
        print('get_total_fee_on_block is called')
        transactions = block['transactions']
        result = 0
        for t in transactions:
            t = json.loads(t)
            is_sbc_t, t_type = self.um.is_sbc_transaction(t)
            if t_type == 'basic':
                total_in = sum(i['transaction']['outputs'][i['output_index']]['value'] for i in t['inputs'])
                total_out = sum(o['value'] for o in t['outputs'])
                delta = total_in  - total_out
                result += delta

        return result

    def check_transactions_in_new_block(self, block):
        """
        ブロック内のTranactionに不正がないか確認する
        """
        fee_for_block = self.get_total_fee_on_block(block)
        fee_for_block += 30
        print("fee_for_block: ", fee_for_block) 
        
        transactions = block['transactions']

        counter = 0

        for t in transactions:
            t = json.loads(t)
            # basic, coinbase_transaction以外はスルーチェック
            is_sbc_t, t_type = self.um.is_sbc_transaction(t)
            if is_sbc_t:
                if t_type == 'basic':
                    if self._check_availability_of_transaction_in_block(t) is not True:
                        print('Bad Block. Having invalid Transaction')
                        return False
                elif t_type == 'coinbase_transaction':
                    if counter != 0:
                        print('Coinbase Transaction is only for BlockBuilder')
                        return False
                    else:
                        insentive = t['outputs'][0]['value']
                        print('insentive', insentive) 
                        if insentive != fee_for_block:
                            print('Invalid value in fee for CoinbaseTransaction', insentive)
                            return False
            else:
                is_verified = self.rsa_util.verify_general_transaction_sig(t)
                if is_verified is not True:
                    return False

        print('ok. this block is acceptable.')
        return True

    def __core_api(self, request, message):

        if request == 'send_message_to_all_peer':
            new_message = self.cm.get_message_text(MSG_ENHANCED, message)
            self.cm.send_msg_to_all_peer(new_message)
            return 'ok'
        elif request == 'send_message_to_all_edge':
            new_message = self.cm.get_message_text(MSG_ENHANCED, message)
            self.cm.send_msg_to_all_edge(new_message)
            return 'ok'
        elif request == 'api_type':
            return 'server_core_api'
        elif request == 'send_message_to_this_pubkey_address':
            print('send_message_to_this_pubkey_address', message[0])
            msg_type = MSG_ENHANCED
            msg_txt = self.cm.get_message_text(msg_type, message[1])
            check_result, target_host, target_port = self.cm.has_this_edge(message[0])
            print('check_result', check_result)
            if check_result:
                print('sending cipher direct message to... ', target_host, target_port)
                self.cm.send_msg((target_host, target_port), msg_txt)
                return 'ok'
            else:
                return None


    def __handle_message(self, msg, is_core, peer=None):
        if peer != None:
            if msg[2] == MSG_REQUEST_FULL_CHAIN:
                print('Send our latest blockchain for reply to : ', peer)
                mychain = self.bm.get_my_blockchain()
                chain_data = pickle.dumps(mychain, 0).decode()
                new_message = self.cm.get_message_text(RSP_FULL_CHAIN, chain_data)
                self.cm.send_msg(peer, new_message)
        else:
            if msg[2] == MSG_NEW_TRANSACTION:
                new_transaction = json.loads(msg[4])
                print('received new_transaction',new_transaction)
                is_sbc_t, t_type = self.um.is_sbc_transaction(new_transaction)
                current_transactions = self.tp.get_stored_transactions()
                if new_transaction in current_transactions:
                    print('this is already pooled transaction: ', new_transaction)
                    return

                    if not is_sbc_t:
                        print('this is not SimpleBitcoin transaction: ', new_transaction)
                        is_verified = self.rsa_util.verify_general_transaction_sig(new_transaction)
                        if not is_verified:
                            print('Transaction Verification Error')
                            return
                    else:
                        # テスト用に最初のブロックだけ未知のCoinbaseTransactionを許すための暫定処置
                        if self.bm.get_my_chain_length() != 1:
                            checked = self._check_availability_of_transaction(new_transaction)
                            if not checked:
                                print('Transaction Verification Error')
                                return
                    self.tp.set_new_transaction(new_transaction)
                    
                    if not is_core:
                        m_type = MSG_NEW_TRANSACTION
                        new_message = self.cm.get_message_text(m_type, json.dumps(new_transaction))
                        self.cm.send_msg_to_all_peer(new_message)
                else:
                    if not is_sbc_t:
                        print('this is not SimpleBitcoin transaction: ', new_transaction)
                        is_verified = self.rsa_util.verify_general_transaction_sig(new_transaction)
                        if not is_verified:
                            return
                    else:
                        # テスト用に最初のブロックだけ未知のCoinbaseTransactionを許すための暫定処置
                        if self.bm.get_my_chain_length() != 1:
                            checked = self._check_availability_of_transaction(new_transaction)
                            if not checked:
                                print('Transaction Verification Error')
                                return
                    self.tp.set_new_transaction(new_transaction)

                    if not is_core:
                        m_type = MSG_NEW_TRANSACTION
                        new_message = self.cm.get_message_text(m_type, json.dumps(new_transaction))
                        self.cm.send_msg_to_all_peer(new_message)                    

            elif msg[2] == MSG_NEW_BLOCK:

                if not is_core:
                    print('block received from unknown')
                    return

                new_block = json.loads(msg[4])
                print('new_block: ', new_block)
                if self.bm.is_valid_block(self.prev_block_hash, new_block):
                    block_check_result = self.check_transactions_in_new_block(new_block)
                    print('block_check_result : ', block_check_result)
                    if not block_check_result:
                        print('previous block hash is ok. but still not acceptable.')
                        self.get_all_chains_for_resolve_conflict()
                        return
                    # ブロック生成が行われていたら一旦停止してあげる（threadingなのでキレイに止まらない場合あり）
                    if self.is_bb_running:
                        self.flag_stop_block_build = True
                    self.prev_block_hash = self.bm.get_hash(new_block)
                    self.bm.set_new_block(new_block)
                else:
                    #　ブロックとして不正ではないがVerifyにコケる場合は自分がorphanブロックを生成している
                    #　可能性がある
                    self.get_all_chains_for_resolve_conflict()

            elif msg[2] == RSP_FULL_CHAIN:

                if not is_core:
                    print('blockchain received from unknown')
                    return

                # ブロックチェーン送信要求に応じて返却されたブロックチェーンを検証し、有効なものか検証した上で
                # 自分の持つチェインと比較し優位な方を今後のブロックチェーンとして有効化する
                new_block_chain = pickle.loads(msg[4].encode('utf8'))
                result, pool_4_orphan_blocks = self.bm.resolve_conflicts(new_block_chain)
                print('blockchain received')
                if result is not None:
                    self.prev_block_hash = result
                    if len(pool_4_orphan_blocks) != 0:
                        # orphanブロック群の中にあった未処理扱いになるTransactionをTransactionPoolに戻す
                        new_transactions = self.bm.get_transactions_from_orphan_blocks(pool_4_orphan_blocks)
                        for t in new_transactions:
                            self.tp.set_new_transaction(t)
                else:
                    print('Received blockchain is useless...')
                    
            elif msg[2] == MSG_ENHANCED:
                # アプリケーションがP2P Network を単なるトランスポートして使うために独自拡張したメッセージはここで処理する。
                # SimpleBitcoin としてはこの種別は使わない
                print('received enhanced message', msg[4])
                has_same = self.mpm_store.has_this_msg(msg[4])

                if has_same is not True:
                    self.mpm_store.add(msg[4])
                    self.mpmh.handle_message(msg[4], self.__core_api, is_core)

    def __get_myip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
