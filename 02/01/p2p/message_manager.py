from distutils.version import StrictVersion
import json


PROTOCOL_NAME = 'simple_bitcoin_protocol'
MY_VERSION = '0.1.0'

MSG_ADD = 0
MSG_REMOVE = 1
MSG_CORE_LIST = 2
MSG_REQUEST_CORE_LIST = 3
MSG_PING = 4
MSG_ADD_AS_EDGE = 5
MSG_REMOVE_EDGE = 6

ERR_PROTOCOL_UNMATCH = 0
ERR_VERSION_UNMATCH = 1
OK_WITH_PAYLOAD = 2
OK_WITHOUT_PAYLOAD = 3


class MessageManager:

    def __init__(self):
        print('Initializing MessageManager...')

    def build(self, msg_type, my_port=50082, payload=None):

        message = {
            'protocol': PROTOCOL_NAME,
            'version': MY_VERSION,
            'msg_type': msg_type,
            'my_port': my_port
        }

        if payload is not None:
            message['payload'] = payload

        return json.dumps(message)

    def parse(self, msg):

        msg = json.loads(msg)
        msg_ver = StrictVersion(msg['version'])
        
        cmd = msg['msg_type']
        my_port = msg['my_port']
        payload = msg.get('payload')

        if msg['protocol'] != PROTOCOL_NAME:
            return ('error', ERR_PROTOCOL_UNMATCH, None, None, None)
        elif msg_ver > StrictVersion(MY_VERSION):
            return ('error', ERR_VERSION_UNMATCH, None, None, None)
        elif cmd == MSG_CORE_LIST:
            return ('ok', OK_WITH_PAYLOAD, cmd, my_port, payload)
        else:
            return ('ok', OK_WITHOUT_PAYLOAD, cmd, my_port, None)
