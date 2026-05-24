# JFFSYE002
# LCKJOS003

from src.networkProtocols.CleartextProtocol import CleartextProtocol
from src.networkProtocols.EncryptedProtocol import EncryptionProtocol
from src.networkProtocols.ExtendedEncryptionProtocol import ExtendedEncryptionProtocol
from src.ChatProtocol import ChatProtocol
from src.ChatClient import ChatClient
from src import ChatUI
from async_tkinter_loop import async_mainloop
import asyncio

def main():
    print("Hello from network-security-project!")

    #ncry = ncryt(server key, userPrivate)

    # construct encryption class
    # call build_send_packet and send that to server durng handshake
    # call parseResponse on server's handshake response
    # call encryptTransport(payload) to send and
    # call decryptTransport(payload) to recieve  
    
    protocols = {
    "CleartextProtocol" : ChatClient(ChatProtocol(CleartextProtocol())),
    "EncryptionProtocol": ChatClient(ChatProtocol(EncryptionProtocol())),
    "ExtendedEncryptionProtocol": ChatClient(ChatProtocol(ExtendedEncryptionProtocol()))
    }
    
    app = ChatUI.ChatUI(protocols)
    app.async_mainloop()

if __name__ == "__main__":
    main()
