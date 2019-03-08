import Crypto
import Crypto.Random
import hashlib
from Crypto.PublicKey import RSA


# RSAの鍵ペアを生成する
def generate_rsa_key_pair():

    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(2048, random_gen)
    public_key = private_key.publickey()

    return public_key, private_key
    

def main():

    test_txt = 'This is test message for getting understand about digital signature'

    pubkey, privkey = generate_rsa_key_pair()

    hashed = hashlib.sha256(test_txt.encode('utf8')).digest()
    print('hashed :' , hashed)
    
    #公開鍵で暗号化
    encrypto = pubkey.encrypt(test_txt.encode('utf-8'), 0)
    print('encrypto :', encrypto)

    #秘密鍵で復号
    decrypto = privkey.decrypt(encrypto)
    print('decrypto :', decrypto)
    	
    if test_txt == decrypto.decode('utf-8'):
        print('test_txt and decrypto are same!')
        
    #秘密鍵で暗号化
    enc_with_priv = privkey.encrypt(hashed, 0)[0]
    print('enc_with_priv :', enc_with_priv)

    # 公開鍵で復号
    dec_with_pub = pubkey.decrypt(enc_with_priv)s
    print('dec_with_pub :', dec_with_pub)

    if hashed == dec_with_pub:
        print('hashed and dec_with_pub are same!')



if __name__ == '__main__':
    main()    
