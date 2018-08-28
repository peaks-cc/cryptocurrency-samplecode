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
    my_p2p_client = ClientCore(50095, '10.1.1.126',50082)
    my_p2p_client.start()

    sleep(10)

    transaction = { 
        'sender': 'test4',
        'recipient': 'test5',
        'value' : 3
    }
    
    my_p2p_client.send_message_to_my_core_node(MSG_NEW_TRANSACTION,json.dumps(transaction))
    print(json.dumps(transaction))
    transaction2 = { 
        'sender': 'test6',
        'recipient': 'test7',
        'value' : 2
    }
    
    my_p2p_client.send_message_to_my_core_node(MSG_NEW_TRANSACTION,json.dumps(transaction2))

    sleep(10)
	
    transaction3 = { 
        'sender': 'test8',
        'recipient': 'test9',
        'value' : 10
    }

    my_p2p_client.send_message_to_my_core_node(MSG_NEW_TRANSACTION,json.dumps(transaction3))

if __name__ == '__main__':
    main()