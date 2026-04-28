#Encryption Protocol
#should I have a setup method?
import nacl.bindings
import nacl.public

class EncryptionProtocol:
    SERVER_STATIC_PUBLIC_KEY=b'f,^\xc0Cb\xf3\x937\xbf\x11\x14"\xed\x13\x0b\x9f\xe7\xaf;\x94\xb0p\x13\xe1\x94\xdd\x85\xcf\x01\x0bC'
    private_key = None
    public_key = None
    def encrypt(self, msg):
        return msg
    
    def DH(self, private_key, public_key):
        return nacl.bindings.crypto_scalarmult(n=private_key, p=public_key)

    def DH_Generate(self):
        #working
        private = nacl.public.PrivateKey.generate()
        return (private, private.public_key)
    
    def setup(self):
        private_key = nacl.public.PrivateKey.generate()

    def main(self):
        print("test")
        (self.private_key, self.public_key)=self.DH_Generate()
        print(self.private_key) 
        print(self.public_key)
        (self.private_key, self.public_key)=self.DH_Generate()
        print(self.private_key)
        print(self.public_key)


if __name__ == "__main__":
    obj = EncryptionProtocol()
    obj.main()
    
