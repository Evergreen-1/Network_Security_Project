#Encryption Protocol
#should I have a setup method?
import nacl.bindings
import nacl.public
import time
from Crypto.Hash import BLAKE2s
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
    
    def AEAD(self):
        #todo needs both an encrypt and a decrypt version.
        return
    
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
    
    def Hmac(self):
        #todo
        return

    def Kdf(self):
        #todo There are three Kdf()-derived functions to create. 
        # Carefully read the specification for their construction
        return

    def Timestamp(self): #working
        #Timestamp() returns the current systme time of the machine.
        return time.time()
    
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

        t = self.Timestamp()
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




if __name__ == "__main__":
    obj = EncryptionProtocol()
    obj.main()
    
