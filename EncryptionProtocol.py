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
    DEBUG = True

    #Worked example testing keys:
    t_client_private_key = b'\x99x\x93eP\xdd\xb7h\xd5dJ\xc7\xa5~\x83\xbdX\x04M\xe29\x15\xe2\xf1\xe8\xd8VFk0\xf8\xa1'
    t_server_public_key = b'f,^\xc0Cb\xf3\x937\xbf\x11\x14"\xed\x13\x0b\x9f\xe7\xaf;\x94\xb0p\x13\xe1\x94\xdd\x85\xcf\x01\x0bC'
    
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
        if isinstance(counter, int):
            nonce = (b'\x00' * 4) + counter.to_bytes(8, 'little')
        else:
            nonce = (b'\x00' * 4) + int.from_bytes(counter).to_bytes(8, 'little')
        return chacha.encrypt(nonce, plain_text, auth_text)
    
    def AEAD_decrypt(self, key, counter, cipher_text, auth_text):
        chacha = ChaCha20Poly1305(key)
        if isinstance(counter, int):
            nonce = (b'\x00' * 4) + counter.to_bytes(8, 'little')
        else:
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
        #KDF1 Look at WireGaurd paper
        p_random = self.Hmac(key, input)
        t1 = self.Hmac(p_random, b'\x01')
        return t1
    
    def KDF2(self, key, input):
        #KDF2 Look at WireGaurd paper
        p_random = self.Hmac(key, input)
        t1 = self.Hmac(p_random, b'\x01')
        t2 = self.Hmac(p_random, t1 + b'\x02')
        return (t1, t2)
    
    def KDF3(self, key, input):
        #KDF3 Look at WireGaurd paper
        p_random = self.Hmac(key, input) 
        t1 = self.Hmac(p_random, b'\x01')
        t2 = self.Hmac(p_random, t1 + b'\x02')
        t3 = self.Hmac(p_random, t2 + b'\x03')
        return (t1, t2, t3)

    def Timestamp(self, t): #working
        #Timestamp() Returns the TAI64N timestamp of the current time, which is 12 bytes of output, the first 8
        #bytes being a big-endian integer of the number of seconds since 1970 TAI and the last 4 bytes being a
        #big-endian integer of the number of microseconds from the beginning of that second. - From WireGaurd paper
        #NOTE: +10 and e6 were made to comply with worked exapmle, change to +37 and e9 if server doesnt work
        TAI64_OFFSET = (2**62) + 10     # +10 leap seconds to match server time
        seconds = int(t) + TAI64_OFFSET
        nanoseconds = int((t%1) * 1e6)  #modding for remainder and x 10^6 to get whole number of micro-secs
        return seconds.to_bytes(8, 'big') + nanoseconds.to_bytes(4, 'big')
    
    def send_prep(self, Construction, Identifier):
    
        chain_key = self.Hash(Construction)
        hash = self.MixHash(chain_key,Identifier)

        hash = self.MixHash(hash, self.t_server_public_key)
        (E_I_priv, E_I_pub) = self.DH_Generate()
        # debugging - E_I_priv = b'\xac\x03\x18b0\xc4\xf7\xd4*\xa7-\x81&\xfb\xc7\xb3PG0\xae\xa4y0\x90\xe2\xe4\xe2\xa0g\\\x83\xb6'
        # debugging - E_I_pub = b"\xb1\x13\xb4\xd3\x00R'\x8b\x80\xd1\xcc\xc8X\x1bYf(4\xce&\xd0V\xde\x97\xff\xba2$u\x9b\xe3G" 

        chain_key = self.KDF1(chain_key, bytes(E_I_pub))   #linking chain key with ephemeral
        hash = self.MixHash(hash, bytes(E_I_pub))

        (chain_key, key1) = self.KDF2(chain_key, self.DH(bytes(E_I_priv), self.t_server_public_key)) #linking chain key with ephemeral + server key
        msg_static = self.AEAD_encrpyt(key1, 0, self.public_key, hash)  #encrypt
        hash = self.MixHash(hash, msg_static)

        #Debugging
        #print("Pre timestamp Hash test")
        #if (hash == b'\x82\xc6E\xc2\xa3\xf4\xe83\x81\x99_\xf64kx-\xff\x18\x1e9XL:[\xb5N\xdb\x1f\xf4\xafP '):
        #    print(True)
        #else:
        #    print(False)
        #    print(hash)

        (chain_key, key2) = self.KDF2(chain_key, self.DH(self.t_client_private_key, self.t_server_public_key))
        # NOTE: In the above example, Timestamp() returned the value 1744377020.21733
        msg_timestamp = self.AEAD_encrpyt(key2, 0, self.Timestamp(time.time()), hash)
        hash = self.MixHash(hash, msg_timestamp)
        return (E_I_pub, msg_static, msg_timestamp, hash)
    
    def recieve_prep(self, chain_key, hash, E_R_pub, E_I_priv, S_I_priv, msg_cipher):
        Q = b'\x00' * 32  # No pre-shared key, set to 0^32 per Wireguard paper

        # chain_key = Kdf1(chain_key, E_R_pub)
        # msg_ephemeral = E_R_pub
        # hash = Hash(hash || msg_ephemeral)
        # chain_key = Kdf1(chain_key, DH(E_I_priv, E_R_pub))
        # chain_key = Kdf1(chain_key, DH(S_I_priv, E_R_pub))
       # (chain_key, tmp, key3) = Kdf3(chain_key, Q)
        # hash = Hash(hash || tmp)
        # msg_empty = AEAD(key3, 0, empty_cipher, hash) — decryption
        # hash = Hash(hash || msg_empty) 
        chain_key = self.KDF1(chain_key, E_R_pub)
        msg_ephemeral = E_R_pub
        hash = self.MixHash(hash, msg_ephemeral)
        chain_key = self.KDF1(chain_key, self.DH(E_I_priv, E_R_pub))
        chain_key = self.KDF1(chain_key, self.DH(S_I_priv, E_R_pub))
        (chain_key, tmp, key3) = self.KDF3(chain_key, Q)
        hash = self.MixHash(hash, tmp)

        msg_text = self.AEAD_decrypt(key3, 0, msg_cipher, hash)
        hash = self.MixHash(hash, msg_text)

    # Section 5.4.5 — Transport Data Key Derivation
        (sending_key, receiving_key) = self.KDF2(chain_key, b'')
        N_send = 0
        N_recv = 0

        return (hash, sending_key, receiving_key, N_send, N_recv, msg_text)


    def testing(self):
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


        #===Send prep testing===
        Constructor = b'Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s'
        Identifier = b'WireGuard v1 zx2c4 Jason@zx2c4.com'

        type = b'\x01'
        reserved = b'\x00'*3
        sender = 4001697114 # Random number, fixed for this worked example

        cl_priv_key_obj = nacl.public.PrivateKey(self.t_client_private_key)
        self.public_key = bytes(cl_priv_key_obj.public_key)
        (E_I_pub, msg_static, msg_timestamp, hash) = self.send_prep(Constructor, Identifier)
        ephemeral = E_I_pub
        static = msg_static
        timestamp = msg_timestamp
        msg = b"\x01\x00\x00\x00Z\r\x85\xee\xb1\x13\xb4\xd3\x00R'\x8b\x80\xd1\xcc\xc8X\x1bYf(4\xce&\xd0V\xde\x97\xff\xba2$u\x9b\xe3G\xc7\x12ry\x04\xb9\xc3\xaf\x9a\xf4\x7f \xf1\x98\xf3rA\x9d\x92\x0f\xaea[=\xf5N\xe0]Q\x9a\x88\x855\xb046\xb5\xefk\xf4z\xcd#\x0c\x0c\xcd<\xda\xc6?XF\x845JvXfm\xf9\xfa0\xf4\xb2\x18\xd6\xf9\x046\x17z\x08\x16y\xa9\xa5"

        out = b'r\xdb\rg\x14\xa2\xff\x13h\xf8K\x9dL\xec\x81\xbf\xa6Q\x15\xf3\xeb\xd7{\x87\xa5\x8bs\xc8\xb4k\x8e\x1e'
        t_send = True if hash == out else False
        print(t_send)
        print(hash)
        out_timestamp = b'\xc6?XF\x845JvXfm\xf9\xfa0\xf4\xb2\x18\xd6\xf9\x046\x17z\x08\x16y\xa9\xa5'
        t_send = True if msg_timestamp == out_timestamp else False
        print(t_send)
        print(msg_timestamp)
        out_msg = b'\xc7\x12ry\x04\xb9\xc3\xaf\x9a\xf4\x7f \xf1\x98\xf3rA\x9d\x92\x0f\xaea[=\xf5N\xe0]Q\x9a\x88\x855\xb046\xb5\xefk\xf4z\xcd#\x0c\x0c\xcd<\xda'
        t_send = True if msg_static == out_msg else False
        print(t_send)
        print(msg_static)
        print("===Send===")
        mac1 = self.Mac(self.Hash(b"mac1----" + self.t_server_public_key), msg)
        mac2 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


         #===Recieve prep testing===
        chain_key = b'\xe0\\UH\\\x12\x9a\xb4\xcc\xd0\r\xa9\xd2\xac\xc7\xb1]ky\xdc\xc2\x18\xb8\x95]NQ\xf9=\xcd\xa5\xc3'
        hash      = b'r\xdb\rg\x14\xa2\xff\x13h\xf8K\x9dL\xec\x81\xbf\xa6Q\x15\xf3\xeb\xd7{\x87\xa5\x8bs\xc8\xb4k\x8e\x1e'

        # Generated server response packet
        response_msg = b'\x02\x00\x00\x00D\xe6+\xe3Z\r\x85\xee\xe5\xd0!\x98z\x12\xb5\xf8&\x17\xfe\x14K\x9exe(\x1bK\xc2\x8e\x15T\x81\xcc\xbe\xceq$\x82v\x7f\x0b\xa1\xfc>\xdf\xb4\xe0\x96Pc\x15\xfe\x9b7\xdc\xb1\x18l\xa4sk\xfd"r\xa5z\x03\x1eu\xdd=\xd9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        # Use the hex output from the generator above
        #response_msg = bytes.fromhex("0200000044e62be35a0d85eee5d021987a12b5f82617fe144b9e7865281b4bc28e155481ccbece712482767f43409ec8e0d79a9d719da92ffb16dfd207b5732006881efe0a")
        # Parse fields
        E_R_pub          = response_msg[12:44]
        msg_empty_cipher = response_msg[44:60]  # 16-byte auth tag

        E_I_priv = b'\xac\x03\x18b0\xc4\xf7\xd4*\xa7-\x81&\xfb\xc7\xb3PG0\xae\xa4y0\x90\xe2\xe4\xe2\xa0g\\\x83\xb6'
        S_I_priv = self.t_client_private_key

        (hash, sending_key, receiving_key, N_send, N_recv, msg_text) = self.recieve_prep(chain_key, hash, E_R_pub, E_I_priv, S_I_priv, msg_empty_cipher)

        # Verify
        assert sending_key   == b'\xd0\x98\xff\xa8\xf4u&\xc4$\x94\xcd&*X\xbfc\x91_\xc3ls\xd1\x1f\xff=\xd4<\x92\xc6\xb5\xb0q'
        assert receiving_key == b'\x032\xb2\xbe\xae"<\'}\x97\x08@w\x98\x10l\xb9\xd4|\xc7\x02\xc4\xefE\x18K\x05\x92\xe0d\x8e\xce'
        print(True)
        print(hash)
        print(msg_text)
        print("===Receive Complete===")


    def main(self):
        if self.DEBUG:
            print("Testing")
            self.testing()

        print("Main")




if __name__ == "__main__":
    obj = EncryptionProtocol()
    obj.main()
    
