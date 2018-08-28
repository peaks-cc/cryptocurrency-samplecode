import signal
from time import sleep
import json

from core.client_core import ClientCore
from p2p.message_manager import MSG_NEW_TRANSACTION


my_p2p_client = None


def signal_handler(signal, frame):
    shutdown_client()

def shutdown_client():
    global my_p2p_client
    my_p2p_client.shutdown()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    global my_p2p_client
    my_p2p_client = ClientCore(50088, '10.1.1.126',50082)
    my_p2p_client.start()

    sleep(10)

    transaction = { 
        'sender': 'test1',
        'recipient': 'test2',
        'value' : 3
    }
    
    my_p2p_client.send_message_to_my_core_node(MSG_NEW_TRANSACTION,json.dumps(transaction))

    transaction2 = { 
        'sender': 'test1',
        'recipient': 'test3',
        'value' : 2
    }
    
    my_p2p_client.send_message_to_my_core_node(MSG_NEW_TRANSACTION,json.dumps(transaction2))

    sleep(10)
	
    transaction3 = { 
        'sender': 'test5',
        'recipient': 'test6',
        'value' : 10
    }

    my_p2p_client.send_message_to_my_core_node(MSG_NEW_TRANSACTION,json.dumps(transaction3))

if __name__ == '__main__':
    main()