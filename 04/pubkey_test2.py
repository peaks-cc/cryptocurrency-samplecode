import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import binascii


# RSAの鍵ペアを生成する
def generate_rsa_key_pair():

    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(2048, random_gen)
    public_key = private_key.publickey()

    return public_key, private_key


# 与えられた秘密鍵を使ってメッセージに署名する    
def compute_digital_signature(message, private_key):
    # まずメッセージをハッシュ値に変換する
    hashed_message = SHA256.new(message.encode('utf8'))
    # 署名にはRSASSA-PKCS1-v1_5を利用する
    signer = PKCS1_v1_5.new(private_key)
    return binascii.hexlify(signer.sign(hashed_message)).decode('ascii')
    
def verify_signature(message, signature, pub_key):
    hashed_message = SHA256.new(message.encode('utf8'))
    verifier = PKCS1_v1_5.new(pub_key)
    return verifier.verify(hashed_message, binascii.unhexlify(signature))     

def main():

    test_txt = 'This is test message for getting understand about digital signature'

    pubkey, privkey = generate_rsa_key_pair()

    # 本来はデジタル署名を使う
    signed = compute_digital_signature(test_txt, privkey)
    print('signed :', signed)
    
    result = verify_signature(test_txt, signed, pubkey)
    
    print('result :' , result)


if __name__ == '__main__':
    main()    
