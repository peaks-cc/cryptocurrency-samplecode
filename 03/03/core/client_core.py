import socket

from p2p.connection_manager_4edge import ConnectionManager4Edge
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
from p2p.message_manager import (

    MessageManager,

    RSP_FULL_CHAIN,
    MSG_ENHANCED,
)

STATE_INIT = 0
STATE_ACTIVE = 1
STATE_SHUTTING_DOWN = 2


class ClientCore:

    def __init__(self, my_port=50082, core_host=None, core_port=None):
        self.client_state = STATE_INIT
        print('Initializing server...')
        self.my_ip = self.__get_myip()
        print('Server IP address is set to ... ', self.my_ip)
        self.my_port = my_port
        self.my_core_host = core_host
        self.my_core_port = core_port
        self.cm = ConnectionManager4Edge(self.my_ip, self.my_port, core_host, core_port, self.__handle_message)
        self.mpm = MyProtocolMessageHandler()
        self.my_protocol_message_store = []

    def start(self):
        self.client_state = STATE_ACTIVE
        self.cm.start()
        self.cm.connect_to_core_node()

    def shutdown(self):
        self.client_state = STATE_SHUTTING_DOWN
        print('Shutdown edge node ...')
        self.cm.connection_close()

    def get_my_current_state(self):
        return self.client_state

    def send_message_to_my_core_node(self, msg_type, msg):
        msg_txt = self.cm.get_message_text(msg_type, msg)
        print(msg_txt)
        self.cm.send_msg((self.my_core_host, self.my_core_port), msg_txt)

    def __client_api(self, request, message):

        if request == 'pass_message_to_client_application':
            self.my_protocol_message_store.append(message)
        elif request == 'api_type':
            return 'client_core_api'
        else:
            print('not implemented api was used')

    def get_my_protocol_messages(self):

        if self.my_protocol_message_store != []:
            return self.my_protocol_message_store
        else:
            return None

    def __handle_message(self, msg):
        if msg[2] == RSP_FULL_CHAIN:
            # TODO: ブロックチェーン送信要求に応じて返却されたブロックチェーンを検証する処理を呼び出す
            pass
        elif msg[2] == MSG_ENHANCED:
            # P2P Network を単なるトランスポートして使っているアプリケーションが独自拡張したメッセージはここで処理する。SimpleBitcoin としてはこの種別は使わない
            self.mpm.handle_message(msg[4], self.__client_api, True)

    def __get_myip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
