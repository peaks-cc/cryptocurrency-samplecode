import signal
import sys
from core.server_core import ServerCore


my_p2p_server = None

def signal_handler(signal, frame):
    shutdown_server()

def shutdown_server():
    global my_p2p_server
    my_p2p_server.shutdown()


def main(my_port, c_host, c_port, p_phrase):
    signal.signal(signal.SIGINT, signal_handler)
    global my_p2p_server
    my_p2p_server = ServerCore(my_port, c_host, c_port, p_phrase)
    my_p2p_server.start()
    my_p2p_server.join_network() 

if __name__ == '__main__':

    args = sys.argv
 
    if len(args) == 5:
        my_port = int(args[1])
        c_host = args[2]
        c_port = int(args[3])
        p_phrase = args[4]
    else:
        print('Param Error')
        print('$ SmpleServer2.py <my_port> <core_node_ip_address> <core_node_port_num> <pass_phrase_for_keys>')
        quit()

    main(my_port, c_host, c_port, p_phrase)