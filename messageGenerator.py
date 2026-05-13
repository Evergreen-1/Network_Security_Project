from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import hashlib

def generate_custom_response():
    # 1. State exactly as it was after the Initiation message
    chain_key = b'\xe0\\UH\\\x12\x9a\xb4\xcc\xd0\r\xa9\xd2\xac\xc7\xb1]ky\xdc\xc2\x18\xb8\x95]NQ\xf9=\xcd\xa5\xc3'
    handshake_hash = b'r\xdb\rg\x14\xa2\xff\x13h\xf8K\x9dL\xec\x81\xbf\xa6Q\x15\xf3\xeb\xd7{\x87\xa5\x8bs\xc8\xb4k\x8e\x1e'
    
    # 2. Worked Example Values
    E_R_pub = b'\xe5\xd0!\x98z\x12\xb5\xf8&\x17\xfe\x14K\x9exe(\x1bK\xc2\x8e\x15T\x81\xcc\xbe\xceq$\x82v\x7f'
    
    # Helper functions
    def Hash(data): return hashlib.blake2s(data, digest_size=32).digest()
    def Hmac(key, data): return hashlib.blake2s(data, key=key, digest_size=32).digest()
    
    # 3. Step-by-step state updates (Page 11)
    # chain_key = Kdf1(chain_key, E_R_pub)
    chain_key = Hmac(Hmac(chain_key, E_R_pub), b'\x01')
    # hash = Hash(hash || E_R_pub)
    handshake_hash = Hash(handshake_hash + E_R_pub)
    
    # 4. Apply the two DH jumps from the worked example
    # DH(E_I_priv, E_R_pub)
    chain_key = b'M$O@\x8e\xc9\x17\x86Y\xf1\xc4\xa5#\xdb\x00\xf7\xf8\xf7B\x0fw\x83\xbe\xcbZ$\x1c\x0b\xcd\xe7\xdf\xbc'
    # DH(S_I_priv, E_R_pub)
    chain_key = b'Y\xbb\xe2\xa1\xfe3\x88E\x96\x86\xc0\xfa\x7f\x0f\xfb~s`f\xc1p\x9c\xbd3\x96\xd8\xb0\x99\x15\xdaL\xbd'
    
    # 5. Derive key3 (KDF3)
    prk = Hmac(chain_key, b'\x00' * 32)
    t1 = Hmac(prk, b'\x01')
    tmp = Hmac(prk, t1 + b'\x02')
    key3 = Hmac(prk, tmp + b'\x03')
    
    # 6. Update hash with tmp BEFORE encrypting
    handshake_hash = Hash(handshake_hash + tmp)
    
    # 7. Encrypt "SOS-PALGS"
    # The current 'handshake_hash' is the 'auth_text' for AEAD
    chacha = ChaCha20Poly1305(key3)
    payload = b"SOS-PALGS"
    msg_cipher = chacha.encrypt(b'\x00' * 12, payload, handshake_hash)
    
    # 8. Construct Packet
    msg_type = b'\x02\x00\x00\x00'
    sender = (3811305028).to_bytes(4, 'little')
    receiver = (4001697114).to_bytes(4, 'little')
    
    return msg_type + sender + receiver + E_R_pub + msg_cipher

print(generate_custom_response().hex())