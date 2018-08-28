import socket

from p2p.connection_manager import ConnectionManager
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
from p2p.message_manager import (
    MessageManager,
    MSG_NEW_TRANSACTION,
    MSG_NEW_BLOCK,
    RSP_FULL_CHAIN,
    MSG_ENHANCED,
)

STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3


class ServerCore:

    def __init__(self, my_port=50082, core_node_host=None, core_node_port=None):
        self.server_state = STATE_INIT
        print('Initializing server...')
        self.my_ip = self.__get_myip()
        print('Server IP address is set to ... ', self.my_ip)
        self.my_port = my_port
        self.cm = ConnectionManager(self.my_ip, self.my_port, self.__handle_message)
        self.mpm = MyProtocolMessageHandler()
        self.core_node_host = core_node_host
        self.core_node_port = core_node_port
        self.my_protocol_message_store = []

    def start(self):
        """
            Coreノードとしての待受を開始する（上位UI層向け
        """
        self.server_state = STATE_STANDBY
        self.cm.start()

    def join_network(self):
        """
            事前に取得した情報に従い拠り所となる他のCoreノードに接続する（上位UI層向け
        """
        if self.core_node_host is not None:
            self.server_state = STATE_CONNECTED_TO_NETWORK
            self.cm.join_network(self.core_node_host, self.core_node_port)
        else:
            print('This server is runnning as Genesis Core Node...')

    def shutdown(self):
        """
            待ち受け状態のServer Socketを閉じて終了する（上位UI層向け
        """
        self.server_state = STATE_SHUTTING_DOWN
        print('Shutdown server...')
        self.cm.connection_close()

    def get_my_current_state(self):
        """
            現在のCoreノードの状態を取得する（上位UI層向け。多分使う人いない
        """
        return self.server_state

    def __core_api(self, request, message):
        """
            MyProtocolMessageHandlerで呼び出すための拡張関数群（現状未整備）

            params:
                request : MyProtocolMessageHandlerから呼び出されるコマンドの種別
                message : コマンド実行時に利用するために引き渡されるメッセージ
        """

        msg_type = MSG_ENHANCED

        if request == 'send_message_to_all_peer':
            new_message = self.cm.get_message_text(msg_type, message)
            self.cm.send_msg_to_all_peer(new_message)
            return 'ok'
        elif request == 'send_message_to_all_edge':
            new_message = self.cm.get_message_text(msg_type, message)
            self.cm.send_msg_to_all_edge(new_message)
            return 'ok'
        elif request == 'api_type':
            return 'server_core_api'

    def __handle_message(self, msg, peer=None):
        """
            ConnectionManagerに引き渡すコールバックの中身。
        """
        if peer is not None:
            # TODO: 現状はMSG_REQUEST_FULL_CHAINの時にしかこの処理に入らないけど、
            # まだブロックチェーンを作るところまで行ってないのでとりあえず口だけ作っておく
            print('Send our latest blockchain for reply to : ', peer)
        else:
            if msg[2] == MSG_NEW_TRANSACTION:
                # TODO: 新規transactionを登録する処理を呼び出す
                pass
            elif msg[2] == MSG_NEW_BLOCK:
                # TODO: 新規ブロックを検証する処理を呼び出す
                pass
            elif msg[2] == RSP_FULL_CHAIN:
                # TODO: ブロックチェーン送信要求に応じて返却されたブロックチェーンを検証する処理を呼び出す
                pass
            elif msg[2] == MSG_ENHANCED:
                # P2P Network を単なるトランスポートして使っているアプリケーションが独自拡張したメッセージはここで処理する。
                # SimpleBitcoin としてはこの種別は使わない

                # あらかじめ重複チェック（ポリシーによる。別にこの処理しなくてもいいかも
                print('received enhanced message', msg[4])
                current_messages = self.my_protocol_message_store
                has_same = False
                if not msg[4] in current_messages:
                    self.my_protocol_message_store.append(msg[4])
                    self.mpm.handle_message(msg[4], self.__core_api)

    def __get_myip(self):
        """
            Google先生から自分のIPアドレスを取得する。内部利用のみを想定
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
