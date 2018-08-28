# -*- coding: utf-8 -*-
import json

# 独自に拡張したGENERALメッセージの処理や生成を担当する
class MyProtocolMessageHandler(object):

	def __init__(self):
		print('Initializing MyProtocolMessageHandler...')

	def handle_message(self, msg):
		msg = json.loads(msg)
		print(msg)
		return

