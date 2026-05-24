# KRNRUA001
# JFFSYE002
# LCKJOS003

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
    
    app = ChatUI.ChatUI()
    app.async_mainloop()

if __name__ == "__main__":
    main()
