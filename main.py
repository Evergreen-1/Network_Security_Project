# JFFSYE002
# LCKJOS003

import EncryptionProtocol
import ChatProtocol
import ChatUI

def main():
    print("Hello from network-security-project!")
    ChatUI.customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
    ChatUI.customtkinter.set_default_color_theme("FlaresOfTheBlazingSun.json")

    #ncry = ncryt(server key, userPrivate)

    # construct encryption class
    # call build_send_packet and send that to server durng handshake
    # call parseResponse on server's handshake response
    # call encryptTransport(payload) to send and
    # call decryptTransport(payload) to recieve
    
    app = ChatUI.ChatUI()
    app.mainloop()

if __name__ == "__main__":
    main()
