import signal
from time import sleep
import json

from core.client_core import ClientCore
from p2p.message_manager import MSG_ENHANCED

my_p2p_client = None


def signal_handler(signal, frame):
    shutdown_client()


def shutdown_client():
    global my_p2p_client
    my_p2p_client.shutdown()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    global my_p2p_client
    my_p2p_client = ClientCore(50098, '10.1.1.126', 50090)
    my_p2p_client.start()

    sleep(10)

    message = {
        'from':'hoge',
        'to':'fuga',
    	'message' :'test'
    }

    my_p2p_client.send_message_to_my_core_node(MSG_ENHANCED,json.dumps(message))


if __name__ == '__main__':
    main()