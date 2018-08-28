import json

SEND_TO_ALL_PEER = 'send_message_to_all_peer'
SEND_TO_ALL_EDGE = 'send_message_to_all_edge'
SEND_TO_THIS_ADDRESS = 'send_message_to_this_pubkey_address'

PASS_TO_CLIENT_APP = 'pass_message_to_client_application'    

class MyProtocolMessageHandler:
    """
    独自に拡張したENHANCEDメッセージの処理や生成を担当する
    """

    def __init__(self):
        print('Initializing MyProtocolMessageHandler...')

    def handle_message(self, msg, api, is_core):
        """
        とりあえず受け取ったメッセージを自分がCoreノードならブロードキャスト、
        Edgeならコンソールに出力することでメッセっぽいものをデモ

        params:
            msg : 拡張プロトコルで送られてきたJSON形式のメッセージ
            api : ServerCore(or ClientCore）側で用意されているAPI呼び出しのためのコールバック
            api(param1, param2) という形で利用する

            is_core : 送信元ノードがCoreノードであるかどうか
        """
        msg = json.loads(msg)
        my_api = api('api_type', None)
        print('my_api: ', my_api)
        if my_api == 'server_core_api':
            if msg['message_type'] == 'cipher_message':
                print('received cipher message!')
                target_address = msg['recipient']
                result = api(SEND_TO_THIS_ADDRESS, (target_address, json.dumps(msg)))
                if result == None:
                    if is_core is not True:
                        api(SEND_TO_ALL_PEER, json.dumps(msg))
            else:
                print('Bloadcasting ...', json.dumps(msg))
                if is_core is not True:
                    # Coreノードからのメッセージでない時だけ他のCoreノードにもブロードキャストする
                    api(SEND_TO_ALL_PEER, json.dumps(msg))
                api(SEND_TO_ALL_EDGE, json.dumps(msg))
        else:
            print('MyProtocolMessageHandler received ', msg)
            api(PASS_TO_CLIENT_APP, msg)

        return
