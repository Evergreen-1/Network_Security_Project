#Encryption Protocol
#should I have a setup method?
import nacl.bindings
import nacl.public
import time
from Crypto.Hash import BLAKE2s
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import hashlib

class EncryptionProtocol:
    SERVER_STATIC_PUBLIC_KEY=b'f,^\xc0Cb\xf3\x937\xbf\x11\x14"\xed\x13\x0b\x9f\xe7\xaf;\x94\xb0p\x13\xe1\x94\xdd\x85\xcf\x01\x0bC'
    private_key = None
    public_key = None
    def encrypt(self, msg):
        return msg
    
    def DH(self, private_key, public_key): #working
        # The Private & Public key input parameters need to be parsed in bytes via bytes() function.
        return nacl.bindings.crypto_scalarmult(n=private_key, p=public_key)

    def DH_Generate(self): #working
        # DH_Generate() generates a private public key pair. 
        private = nacl.public.PrivateKey.generate()
        return (private, private.public_key)
    
    def AEAD_encrpyt(self, key, counter, plain_text, auth_text):
        #todo needs both an encrypt and a decrypt version.
        chacha = ChaCha20Poly1305(key)
        nonce = (b'\x00' * 4) + int.from_bytes(counter).to_bytes(8, 'little')
        return chacha.encrypt(nonce, plain_text, auth_text)
    
    def AEAD_decrypt(self, key, counter, cipher_text, auth_text):
        chacha = ChaCha20Poly1305(key)
        nonce = (b'\x00' * 4) + int.from_bytes(counter).to_bytes(8, 'little')
        return chacha.decrypt(nonce, cipher_text, auth_text)
    
    def Hash(self, message): #working
        #Using Blake2s from WireGuard Paper
        #Note: the message it takes is a string, does allow for either inputs but it needs to be encoded with UTF-8
        if isinstance(message, bytes):
            data = message
        else:
            data = message.encode("UTF-8")
        hash_obj = hashlib.blake2s(digest_size=32)
        hash_obj.update(data)
        return  hash_obj.digest()

    def MixHash(self, message1, message2):  #working
        #todo This function is not defined in the paper, but will be a useful convenience function 
        # because a number of operations require the hash of concatenated inputs. 
        # Use whenever you see Hash(.. || ..) in the paper.
        message = message1 + message2
        return self.Hash(message)
    
    def Mac(self, key, input): #working
        #todo
        #Allows bytes or string input
        if isinstance(input, bytes):
            data = input
        else:
            data = input.encode("UTF-8")
        mac_obj = hashlib.blake2s(data=data, key=key, digest_size=16)
        return mac_obj.digest()
    
    def Hmac(self, key, input): #working
        # HMac(key, input) = H((K' XOR opad) || H((K' XOR ipad) || input))
        # Where K'= {H(K) if len(K) > blocksize; else K }

        if len(key) > 64:   # getting K'
            key_p = self.Hash(key)
        else:
            key_p = key + (b'\x00' * (64 - len(key)))  # pad right to 64 bytes

        outer = bytes(a ^ b for a, b in zip(key_p, b'\x5c' * 64))   # getting K' XOR outer pad
        inner = bytes(a ^ b for a, b in zip(key_p, b'\x36' * 64))   # getting K' XOR inner pad

        return self.Hash(outer + self.Hash(inner + input)) 


    def KDF1(self, key, input):
        #todo There are three Kdf()-derived functions to create. 
        # Carefully read the specification for their construction
        p_random = self.Hmac(key, input)
        t1 = self.Hmac(p_random, b'\x01')
        return t1
    
    def KDF2(self, key, input):
        #todo There are three Kdf()-derived functions to create. 
        # Carefully read the specification for their construction
        p_random = self.Hmac(key, input)
        t1 = self.Hmac(p_random, b'\x01')
        t2 = self.Hmac(p_random, t1 + b'\x02')
        return (t1, t2)
    
    def KDF3(self, key, input):
        #todo There are three Kdf()-derived functions to create. 
        # Carefully read the specification for their construction
        p_random = self.Hmac(key, input) 
        t1 = self.Hmac(p_random, b'\x01')
        t2 = self.Hmac(p_random, t1 + b'\x02')
        t3 = self.Hmac(p_random, t2 + b'\x03')
        return (t1, t2, t3)

    def Timestamp(self, t): #working
        #Timestamp() Returns the TAI64N timestamp of the current time, which is 12 bytes of output, the first 8
        #bytes being a big-endian integer of the number of seconds since 1970 TAI and the last 4 bytes being a
        #big-endian integer of the number of nanoseconds from the beginning of that second. - From WireGaurd paper
        seconds = int(t)
        nanoseconds = int((t%1) * 1e9)  #modding for remainder and x 10^9 to get whole number of nano-secs
        return seconds.to_bytes(8, 'big') + nanoseconds.to_bytes(4, 'big')
    
    def send_prep(self, msg):
        #main test for now
        # chain_key = Hash(Construction)

        # hash = Hash(chain_key || Identifier)

        # hash = Hash(hash || S_R_pub)

        # (E_I_priv, E_I_pub) = DH-Generate()

        # chain_key = Kdf1(chain_key, E_I_pub)

        # hash = Hash(hash || E_I_pub)

        # (chain_key, key1) = Kdf2(chain_key, DH(E_I_priv, S_R_pub))

        # msg_static = AEAD(key1, 0, S_I_pub, hash), an encryption operation

        # hash = Hash(hash || msg_static)

        # (chain_key, key2) = Kdf2(chain_key, DH(S_I_priv, S_R_pub))

        # timestamp = AEAD(key2, 0, Timestamp(), hash), an encryption operation

        # hash = Hash(hash || msg_timestamp)
        return
    
    def recieve_prep(self, msg):
        # The chain_key and hash are maintained through the initiation sequence, 
        # linking the initiation and response messages together:

        # chain_key = Kdf1(chain_key, E_R_pub)

        # msg_ephemeral = E_R_pub

        # Hash(hash || msg_ephemeral)

        # chain_key = Kdf1(chain_key, DH(E_I_priv, E_R_pub))

        # chain_key = Kdf1(chain_key, DH(S_I_priv, E_R_pub))

        # (chain_key, tmp, key3) = Kdf3(chain_key, Q)

        # Hash(hash || tmp)

        # msg_empty = AEAD(key3, 0, empty, hash), a decryption operation

        # Hash(hash || msg_empty)

        return msg
    


    def main(self):
        #testing phase
        print("test")
        (self.private_key, self.public_key)=self.DH_Generate()
        print(self.private_key) 
        print(self.public_key)
        print("===DH_Generate Complete===")

        key = self.DH(bytes(self.private_key), bytes(self.public_key))
        print(key)
        print("===DH_Generate Complete===")

        t = self.Timestamp(time.time())
        print(t)
        print("===TimeStamp Complete===")

        hash_test = self.Hash(b'Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s')
        t_H = True if hash_test == b"`\xe2m\xae\xf3'\xef\xc0.\xc35\xe2\xa0%\xd2\xd0\x16\xebB\x06\xf8rw\xf5-8\xd1\x98\x8bx\xcd6" else False
        print(t_H)
        print("===Hash Complete===")

        input1 = b'a'*50
        input2 = b'b'*50
        t_MH = True if self.MixHash(input1, input2) == b'#B\x17\x17\xbe=\xfcc\xd6\xb5@81\t\x8dh\x88\x9b\xb3\xa8\xb9\xb2n\n\x02\r:\xcb\xbe\xb0\xa7\xee' else False
        print(t_MH)
        print("===MixHash Complete===")

        key_mac = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
        mac_input = b'I am a message without a MAC, but only for now.'
        t_M = True if self.Mac(key_mac, mac_input) == b'*\xbd\x8ak4%\xe4\xb0\xe7\x96\xe5z\x14q\xdd!' else False
        print(t_M)
        print("===Mac Complete===")

        key_hmac = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
        hmac_input = b'I am a message without an HMAC, but only for now.'
        t_HM = True if self.Hmac(key_hmac, hmac_input) == b'\x1ew,:\x03\xdd\x0b\x1e\x96\n\x00J\x8c\xe1QzQ\xff\xb8\x02\xcb\xa29\xa8{\x00\x07(\xa6\xc0\x07\xde' else False
        print(t_HM)
        #print(self.Hmac(key_hmac, hmac_input))
        print("===HMac Complete===")

        key = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
        input = b'Choose your LLM adventure folks.'
        t_KDF1 = True if self.KDF1(key, input) == b'0fO\x0e\x0f\xb2\xf4\xaa\xcc\x14\x9c\x84\x8a\xb0D\xd3i\xa6\xac\xbf\xae\xdc^\xd0-D"64X\x93W' else False
        print(t_KDF1)
        out2 = (b'0fO\x0e\x0f\xb2\xf4\xaa\xcc\x14\x9c\x84\x8a\xb0D\xd3i\xa6\xac\xbf\xae\xdc^\xd0-D"64X\x93W', b'\xaa\x9b\x0fh\xf9\x99z\\%\\\x0f\x8c9L\x7f~<\x1f\xa9G\x9d \x1dw\xba\xc3\x96\x9e\xbb\x8f\x12&')
        t_KDF2 = True if self.KDF2(key, input) == out2 else False
        print(t_KDF2)
        out3 = (b'0fO\x0e\x0f\xb2\xf4\xaa\xcc\x14\x9c\x84\x8a\xb0D\xd3i\xa6\xac\xbf\xae\xdc^\xd0-D"64X\x93W', b'\xaa\x9b\x0fh\xf9\x99z\\%\\\x0f\x8c9L\x7f~<\x1f\xa9G\x9d \x1dw\xba\xc3\x96\x9e\xbb\x8f\x12&', b'\\\xfb\xc9\xf8!\x88\x03\xa1u\xa8!gUk\xfd\x8b4E|\n5\x89\xb1\xb6\xc1\x1a\x8f\xae?\\\xac)')
        t_KDF3 = True if self.KDF3(key, input) == out3 else False
        print(t_KDF3)
        print("===KDF Complete===")


        key = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
        counter = b'\x00'*12 # Read the standard carefully for how this must be formatted
        plaintext = b"attack at dawn"
        authtext = b'\x8e2\x89\xe2\x14\xfd\x16\x19o\x06\xc9\xb2\xd9\xe8F\xfd\xdaf\xdc\xa4\xf9\xe9\x98\xbc\xd8x\xb9\x90\x1e\n\xac\x98'

        outen = b'\xfbv\x84\xea\xd0S\n\xc1\x16\x9et\xd5\xa4/\xeee\x9a\xa9MR\xe3\xd5p3\x85\r\xce\x15r\xcd'
        t_en = True if self.AEAD_encrpyt(key, counter, plaintext, authtext) == outen else False
        print(t_en)
        outde = b'attack at dawn'
        t_de = True if self.AEAD_decrypt(key, counter, outen, authtext) == outde else False
        print(t_de)
        print("===AEAD Complete===")






if __name__ == "__main__":
    obj = EncryptionProtocol()
    obj.main()
    
