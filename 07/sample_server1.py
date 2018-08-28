import signal
import sys

from core.server_core import ServerCore

my_p2p_server = None


def signal_handler(signal, frame):
    shutdown_server()

def shutdown_server():
    global my_p2p_server
    my_p2p_server.shutdown()


def main(my_port, p_phrase):
    signal.signal(signal.SIGINT, signal_handler)
    global my_p2p_server
    # 始原のCoreノードとして起動する
    my_p2p_server = ServerCore(my_port, None, None, p_phrase) 
    my_p2p_server.start()


if __name__ == '__main__':
    args = sys.argv
 
    if len(args) == 3:
        my_port = int(args[1])
        p_phrase = args[2]
    else:
        print('Param Error')
        print('$ SmpleServer1.py <my_port> <pass_phrase_for_keys>')
        quit()

    main(my_port, p_phrase)