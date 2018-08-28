import binascii
import base64

from utils.aes_util import AESUtil
from utils.key_manager import KeyManager

def main():

    my_km = KeyManager()
    target_txt = '猫が寝込んだ'
    print('target text: ', target_txt)
    
    # 暗号化用の鍵を生成してメッセージを暗号化
    aes_util = AESUtil()
    cipher_txt = aes_util.encrypt(target_txt)
    print('cipher_txt : ', base64.b64encode(cipher_txt))

    # 暗号化用の鍵を取り出す
    key = aes_util.get_aes_key()
    print('aes_key : ', binascii.hexlify(key).decode('ascii'))

    # まずは鍵を公開鍵で暗号化
    encrypted_key = my_km.encrypt_with_my_pubkey(key)
    print('encrypted_key : ', binascii.hexlify(encrypted_key[0]).decode('ascii'))
    
    # メッセージデータのJSONに入れ込めるようBase64エンコードした上で文字列化
    key_to_be_send = binascii.hexlify(base64.b64encode(encrypted_key[0])).decode('ascii')
    print('to_be_send', key_to_be_send)
    
    # Base64エンコードされたデータをまずデコードする
    un_hex = base64.b64decode(binascii.unhexlify(key_to_be_send))
    print('un_hex', un_hex)

    # 鍵の取り出し
    decrypted_key2 = my_km.decrypt_with_private_key(un_hex)
    print('decrypted_key : ', binascii.hexlify(decrypted_key2).decode('ascii'))

    # 暗号メッセージの復号
    dec2 = aes_util.decrypt_with_key(cipher_txt, key)
    print('decoded text :', dec2.decode('utf-8'))

if __name__ == '__main__':

    main()