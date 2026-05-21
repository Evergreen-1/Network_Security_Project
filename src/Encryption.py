#Encryption Protocol
import nacl.bindings
import nacl.public
import time
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import hashlib
import random
import base64

class Encryption:
    #Class input varaibles
    SERVER_STATIC_PUBLIC_KEY= None  #Required as input
    client_private_key = None       #NOTE Need to get from website
    client_public_key = None        #Derived from private key    

    #Class varaibles
    sending_key   = None
    receiving_key = None
    N_send        = 0
    N_recv        = 0
    server_index  = None        #The servers index
    client_sender_index = None  #basically sessionID
    hash = None
    chain_key = None  

    def __init__(self, client_private_key=None, SERVER_STATIC_PUBLIC_KEY=None):
        if (client_private_key is None or SERVER_STATIC_PUBLIC_KEY is None):
                raise ValueError("All keys must have values")
        else:
            if isinstance(client_private_key, bytes):
                client_private_key = nacl.public.PrivateKey(client_private_key)
            elif not isinstance(client_private_key, nacl.public.PrivateKey):
                raise TypeError("client_private_key must be bytes or nacl.public.PrivateKey")
            self.SERVER_STATIC_PUBLIC_KEY = SERVER_STATIC_PUBLIC_KEY
            self.client_private_key = client_private_key
            self.client_public_key = bytes(client_private_key.public_key)

            self.sending_key   = None
            self.receiving_key = None
            self.N_send        = 0
            self.N_recv        = 0
            self.server_index  = None        #The servers index
            self.client_sender_index = None  #basically sessionID
            self.hash = None
            self.chain_key = None
    
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
        #NOTE: the message it takes is a string, does allow for either inputs but it needs to be encoded with UTF-8
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

        hash = self.MixHash(hash, self.SERVER_STATIC_PUBLIC_KEY)
        (E_I_priv, E_I_pub) = self.DH_Generate()

        chain_key = self.KDF1(chain_key, bytes(E_I_pub))   #linking chain key with ephemeral
        hash = self.MixHash(hash, bytes(E_I_pub))

        (chain_key, key1) = self.KDF2(chain_key, self.DH(bytes(E_I_priv), self.SERVER_STATIC_PUBLIC_KEY)) #linking chain key with ephemeral + server key
        msg_static = self.AEAD_encrpyt(key1, 0, self.client_public_key, hash)  #encrypt
        hash = self.MixHash(hash, msg_static)

        (chain_key, key2) = self.KDF2(chain_key, self.DH(bytes(self.client_private_key), self.SERVER_STATIC_PUBLIC_KEY))
        # NOTE: In the above example, Timestamp() returned the value 1744377020.21733
        msg_timestamp = self.AEAD_encrpyt(key2, 0, self.Timestamp(time.time()), hash)
        hash = self.MixHash(hash, msg_timestamp)
        return (E_I_pub, E_I_priv, chain_key, msg_static, msg_timestamp, hash)
    
    def recieve_prep(self, chain_key, hash, E_R_pub, E_I_priv, private_key, msg_cipher, Q):
        '''Deciphering response's wireguard protocol'''

        chain_key = self.KDF1(chain_key, E_R_pub)
        hash = self.MixHash(hash, E_R_pub)
        chain_key = self.KDF1(chain_key, self.DH(E_I_priv, E_R_pub))
        chain_key = self.KDF1(chain_key, self.DH(bytes(private_key), E_R_pub))
        (chain_key, tmp, key3) = self.KDF3(chain_key, Q)
        hash = self.MixHash(hash, tmp)

        msg_text = self.AEAD_decrypt(key3, 0, msg_cipher, hash)
        if msg_text != b'': #Debugging
            raise ValueError("Handshake decryption failed: empty payload expected")
        hash = self.MixHash(hash, msg_text)

        return (hash, chain_key)


    def encrypt_transport(self, plaintext):
        '''Encrypting and constructing plain_text into packet
           where msg_packet = AEAD(sending_key, N_send, plaintext, empty_auth)'''
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        ciphertext = self.AEAD_encrpyt(self.sending_key, self.N_send, plaintext, b'')
        # Assemble transport packet
        msg_type       = b'\x04'        #Standard value for Wireguard transport message type according to paper
        reserved       = b'\x00' * 3
        receiver_index = self.server_index.to_bytes(4, 'little')
        counter        = self.N_send.to_bytes(8, 'little')
    
        self.N_send += 1  # increment counter after each message
 
        return msg_type + reserved + receiver_index + counter + ciphertext
    
    def decrypt_transport(self, packet):
        '''Extracting and decrypting packet to get plain_text'''
        counter = int.from_bytes(packet[8:16], 'little')            #NOTE need to verify that slicing is correct
        cipher_text = packet[16:]
        auth_text = b''
        #Calling decrpyt
        plain_text = self.AEAD_decrypt(self.receiving_key, counter, cipher_text, auth_text) 
        self.N_recv += 1

        return plain_text
    
    def build_send_packet(self):
        '''Construct message packet with send_prep in correct format'''
        Construction = b'Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s'
        Identifier   = b'WireGuard v1 zx2c4 Jason@zx2c4.com'

        (E_I_pub, self.E_I_priv, self.chain_key, msg_static, msg_timestamp, self.hash) = self.send_prep(Construction, Identifier)
        #Parameter preperation
        self.client_sender_index = random.randint(0, 2**32 -1)#session ID

        msg = b'\x01'                                   #type (1 byte)
        msg+= b'\x00'*3                                 #reserved (3 bytes)
        msg+= self.client_sender_index.to_bytes(4, 'little') #sender (4 bytes)
        msg+= bytes(E_I_pub)                                   #ephemeral (32 bytes)
        msg+= msg_static                                #static (̂32 bytes)
        msg+= msg_timestamp                             #timestamp (̂12 bytes)
        mac1 = self.Mac(self.Hash(b"mac1----" + self.SERVER_STATIC_PUBLIC_KEY), msg)
        msg+= mac1                                      #mac1 (16 bytes)
        msg+= b'\x00'*16                                #mac2 (16 bytes)

        return msg
    
    def parse_response(self, response):
        '''Manager method to take response and extract components for recieve_prep and decrypt_transport'''
        # Wireguard response layout:
        # [0]     type      (1 byte,  should be 0x02)
        # [1:4]   reserved  (3 bytes)
        # [4:8]   sender    (4 bytes)
        # [8:12]  receiver  (4 bytes)
        # [12:44] ephemeral (32 bytes)
        # [44:60] empty     (16 bytes, encrypted empty + auth tag)
        # [60:76] mac1      (16 bytes)
        # [76:92] mac2      (16 bytes)

        self.server_index = int.from_bytes(response[4:8], 'little')                 #sender (4 bytes)
        assert self.client_sender_index == int.from_bytes(response[8:12], 'little')
        E_R_pub = response[12:44]                                                   #ephemeral (32 bytes)
        empty = response[44:60]                                                     #empty (16 bytes)
        Q = b'\x00'*32

        (hash, chain_key) = self.recieve_prep(self.chain_key, self.hash, E_R_pub, bytes(self.E_I_priv), bytes(self.client_private_key), empty, Q)
        #Transport Data Key Derivation
        (self.sending_key, self.receiving_key) = self.KDF2(chain_key, b'')
        self.N_send = 0
        self.N_recv = 0
        return

'''NetSec Wireguard Project
   
   class ExtendedEncryptionProtocol
   description:
        This class extends the Encryption protocol to adopt the mac2 calculations and the cookie handling.'''
class ExtendedEncryption(Encryption):

    def __init__ (self, client_private_key=None, SERVER_STATIC_PUBLIC_KEY=None):
        super().__init__(client_private_key, SERVER_STATIC_PUBLIC_KEY)
        self.mac1 = None
        self.cookie = None

    def build_send_packet(self, cookie=None):
        msg = super().build_send_packet()
        self.mac1 = msg[-32:-16]    #retriving the mac1 from msg before calculating mac2

        if cookie is not None:
            mac2 = self.Mac(cookie, msg[:-16])
            msg = msg[:-16] + mac2

        return msg

    def parse_cookie_reply(self, response):
        # type 0x03: [0] type, [1:4] reserved, [4:8] receiver,
        # [8:24] nonce, [24:56] encrypted_cookie
        nonce = response[8:24]
        encrypted_cookie = response[24:]
        key = self.Hash(b"cookie--" + self.SERVER_STATIC_PUBLIC_KEY)
        chacha = ChaCha20Poly1305(key)
        self.cookie = chacha.decrypt(nonce, encrypted_cookie, self.mac1)
        return self.cookie
    

if __name__ == "__main__":
    '''TODO Here is some basic input example that needs to me removed for final'''
    server_key = base64.b64decode(b'ZixewENi85M3vxEUIu0TC5/nrzuUsHAT4ZTdhc8BC0M=')
    client_private_key = input("Enter your private key (base64):\n")        #NOTE fill this in if you must
    priv_key = base64.b64decode(client_private_key)
    obj = EncryptionProtocol(priv_key, server_key)
    ext_obj = ExtendedEncryptionProtocol(priv_key, server_key)
        