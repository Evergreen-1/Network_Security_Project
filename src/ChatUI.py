# Main Menu
import customtkinter
from PIL import Image
import os

import threading
import time

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("FlaresOfTheBlazingSun.json")

headingFont = ("Roboto", 24)
msgNameFont = ("Roboto", 18, "bold")
msgTimeFont = ("Roboto", 12)
textColour = '#FEA943'

msgs = (  {"text": "Let's begin. The first decision: A story about a baby bird", "senderName":"Not You", "messageTime" :"00:00", "side":"left"},
        {"text": "This story happened when Robin and I were very young. We were victims of the Stellaron Disaster, and The Family's Mr. Gopher Wood — who would later become the Dreammaster of Penacony — saw that we siblings had no one to turn to and took us in.", "senderName":"Not You", "messageTime": "00:00", "side":"left"},
        {"text" : "Let's begin. The first decision: A story about a baby bird", "senderName": "Not You", "messageTime" : "00:00", "side":"left"},
        {"text" : "Nurture with care in a cage", "senderName": "You", "messageTime" : "00:00", "side":"right"},
        {"text" : "Why do birds fly? They fly because they want to. Even if they don't have a reason. Even if there wings break and they might die. They don't fly for others or because they've been ordered by anyone. They just feel 'I want to fly', and take to the skies on their own. That is my answer. That is who I am.", "senderName": "You", "messageTime" : "00:00", "side":"right"},
        {"text" : "Star Platinum, Za Warudo!!!!", "senderName": "You", "messageTime" : "00:00", "side":"right"}
)

chats = ("chat1", "chat2", "chat3", "chat4")

#        create_bubble(self.messageListFrame, controller, "", side = "left")
#        create_bubble(self.messageListFrame, controller, "Later on, Robin and I lived a time with nary a care in the world. One day, after dinner, while my younger sister and I were lounging about in Mr. Gopher Wood's yard, we spotted a fledgling Charmony Dove all on its own.", side = "left")
#        create_bubble(self.messageListFrame, controller, "That baby bird was tiny, it didn't even have all of its feathers, and it couldn't sing. When we found it, it was already on its last breath, having fallen into a shrub — probably abandoned by its parents.", side = "left")
#        create_bubble(self.messageListFrame, controller, "We decided to build a nest for it right there and then. However, thinking back, that winter was unusually cold, with fierce winds at night in the yard, not to mention the many poisonous bugs and wild beasts in the vicinity.", side = "left")
#        create_bubble(self.messageListFrame, controller, "It was clear that if we left the fledgling in the yard, it stood no chance of surviving until spring. So, I suggested we take it inside, place it on the shelf by the window, and asked the adults to fashion a cage for it.", side = "left")
#        create_bubble(self.messageListFrame, controller, "We decided that when it regained its strength enough to spread its wings, we would release it back into the wild. The tragic part — something that we'd never considered — was that this bird's fate had already been determined long before this moment.", side = "left")
#        create_bubble(self.messageListFrame, controller, "Its destiny was determined by our momentary whim.", side = "left")
#        create_bubble(self.messageListFrame, controller, "Now, I pass the power of choice to you all. Faced with this situation, what choice would you make?", side = "left")
#        create_bubble(self.messageListFrame, controller, "Nurture with care in a cage", side = "right")
#        create_bubble(self.messageListFrame, controller, "Why do birds fly? They fly because they want to. Even if they don't have a reason. Even if there wings break and they might die. They don't fly for others or because they've been ordered by anyone. They just feel 'I want to fly', and take to the skies on their own. That is my answer. That is who I am.", side = "right")
#        create_bubble(self.messageListFrame, controller, "Star Platinum, Za Warudo!!!!", side = "right")

def defaultButton():
    print("button pressed")

class ChatUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        windowWidth = 400
        windowHeight = 240
        
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        scalingFactor = customtkinter.ScalingTracker.get_window_scaling(self)
        x = int(((screenWidth / 2) - (windowWidth / 2)) * scalingFactor)
        y = int(((screenHeight / 2) - (windowHeight / 2)) * scalingFactor)
        self.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
        self.minsize(windowWidth, windowHeight)
        
        self.frames = {}
        self.username = "DefaultNameText"

        for F in (MainMenuFrame, ChattingFrame):
            frameName = F.__name__
            frame = F(parent=self, controller=self)
            frame.place(relx=0.5, rely=0.5, relwidth=0.99, relheight=0.99, anchor="center")
            self.frames[frameName] = frame

        self.changeFrame("MainMenuFrame")

    def changeFrame(self, frameName):
        self.frames[frameName].tkraise()
        match frameName:
            case "MainMenuFrame":
                print("Moving to Main Menu Frame")
                windowWidth = 400
                windowHeight = 240
                screenWidth = self.winfo_screenwidth()
                screenHeight = self.winfo_screenheight()
                scalingFactor = customtkinter.ScalingTracker.get_window_scaling(self)
                x = int(((screenWidth / 2) - (windowWidth / 2)) * scalingFactor)
                y = int(((screenHeight / 2) - (windowHeight / 2)) * scalingFactor)
                self.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
                self.minsize(windowWidth, windowHeight)
            case "ChattingFrame":
                print("Moving to Chatting Frame")
                windowWidth = 1200
                windowHeight = 720
                screenWidth = self.winfo_screenwidth()
                screenHeight = self.winfo_screenheight()
                scalingFactor = customtkinter.ScalingTracker.get_window_scaling(self)
                x = int(((screenWidth / 2) - (windowWidth / 2)) * scalingFactor)
                y = int(((screenHeight / 2) - (windowHeight / 2)) * scalingFactor)
                self.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
                self.minsize(windowWidth, windowHeight)
            case _:
                print("Error!, unknown frame name:", frameName)
                windowWidth = 400
                windowHeight = 240
                screenWidth = self.winfo_screenwidth()
                screenHeight = self.winfo_screenheight()
                scalingFactor = customtkinter.ScalingTracker.get_window_scaling(self)
                x = int(((screenWidth / 2) - (windowWidth / 2)) * scalingFactor)
                y = int(((screenHeight / 2) - (windowHeight / 2)) * scalingFactor)
                self.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
                self.minsize(windowWidth, windowHeight)
                
    def exitChattingApp(self):
        self.destroy()

    def setName(self, name):
        self.username = name

class MainMenuFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.lblTitle = customtkinter.CTkLabel(self, text="NEXXXXXAAAA!!!", font=headingFont, text_color=textColour)
        self.lblTitle.place(relx=0.5, rely=0.15, relwidth=0.5, anchor=customtkinter.CENTER)
        
        self.clearTextChat = customtkinter.CTkButton(self, text="Cleartext Chat", command=lambda: controller.changeFrame("ChattingFrame"))
        self.clearTextChat.place(relx=0.5, rely=0.35, relwidth=0.5, anchor=customtkinter.CENTER)

        self.encryptedChat = customtkinter.CTkButton(self, text="Encrypted Chat", command=defaultButton)
        self.encryptedChat.place(relx=0.5, rely=0.5, relwidth=0.5, anchor=customtkinter.CENTER)

        self.extendedEncryptionChat = customtkinter.CTkButton(self, text="Extended Encryption Chat", command=defaultButton)
        self.extendedEncryptionChat.place(relx=0.5, rely=0.65, relwidth=0.5, anchor=customtkinter.CENTER)
        
        self.buttonExitChattingApp = customtkinter.CTkButton(self, text="EXIT", command=lambda: controller.exitChattingApp())
        self.buttonExitChattingApp.place(relx=0.5, rely=0.8, relwidth=0.5, anchor=customtkinter.CENTER)

class Chatting_UsernameFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.btnChangeUsername = customtkinter.CTkButton(master=self, text="", command=lambda: self.changeUsernameFunc(), fg_color="#242424", 
                                                         hover='#242424')
        self.btnChangeUsername.place(relx=0.9, rely=0.7, relwidth = 0.15, relheight = 0.35, anchor=customtkinter.CENTER)
        
        self.icon = customtkinter.CTkImage(
                       dark_image=Image.open("editIcon.png"),
                       size=(36, 36))

        self.btnChangeUsername.configure(image=self.icon)
        
        self.lblTitle = customtkinter.CTkLabel(self, text=controller.username, font=headingFont, text_color=textColour)
        self.lblTitle.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
    
    def changeUsernameFunc(self):
        print("Changing username")

class Chatting_ChatListFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.chatList = customtkinter.CTkScrollableFrame(master=self)
        self.chatList.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor="center")
        
        for chat in chats:
            newChat = customtkinter.CTkFrame(master=self.chatList)

            btnchatName = customtkinter.CTkButton(newChat, text=chat, font= msgNameFont, command=lambda: self.openChat(chat))
            btnchatName.pack(anchor="center", fill='x', expand=True)
            
            newChat.pack(anchor='center', padx=1, pady=3, fill='x', expand=True)
        
        self.clearTextChat = customtkinter.CTkButton(self, text="Cleartext Chat", command=lambda: controller.changeFrame("ChattingFrame"))
        self.clearTextChat.place(relx=0.5, rely=0.3, anchor=customtkinter.CENTER)

    def openChat(self, chatName):
        print("openChat: ", chatName)

class Chatting_SignOutFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.btnSignOut = customtkinter.CTkButton(self, text="Sign Out", command=lambda: controller.changeFrame("MainMenuFrame"))
        self.btnSignOut.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

def create_bubble(master, controller, text, senderName="You", messageTime="00:00", side="left"):
    # Determine colors based on sender
    fg_color = ("#f08315", "#f08315") if side == "right" else ("#ebebeb", "#f16146")
    text_color = ("black", "white")
    anchor = "e" if side == "right" else "w"
    othranchor = "w" if side == "right" else "e"
    msgFrame = customtkinter.CTkFrame(master, fg_color='transparent', border_width=0)
    lblsenderName = customtkinter.CTkLabel(msgFrame, text=senderName, font=msgNameFont, text_color=textColour)
    lblsenderName.pack(anchor=anchor, pady=0, padx=0)
    bubble = customtkinter.CTkLabel(
        msgFrame,
        text=text, 
        corner_radius=15, 
        fg_color=fg_color,
        text_color=text_color,
        padx=10,
        pady=5,
        wraplength=500 # Ensures text wraps in the bubble
    )
    bubble.pack(anchor=anchor, pady=0, padx=0)
    bubbleWidth = bubble.winfo_width()
    lblmsgTime = customtkinter.CTkLabel(msgFrame, text=messageTime, font=msgTimeFont, text_color=textColour)
    lblmsgTime.pack(anchor=othranchor, pady=0, padx=10)
    #lblmsgTime.pack(anchor=anchor, padx=(bubbleWidth, 0))
    msgFrame.pack(anchor=anchor, pady=0, padx=10)
    return msgFrame

class Chatting_MessageListFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.messageEnterFrame = customtkinter.CTkFrame(master=self)
        self.messageEnterFrame.place(relx=0.5, rely=0.93, relwidth=0.95, relheight=0.1, anchor="center")

        self.msgBox = customtkinter.CTkEntry(master=self.messageEnterFrame, placeholder_text="Enter your message here.")
        self.msgBox.place(relx=0.45, rely=0.5, relwidth=0.88, relheight=0.8, anchor="center")

        self.btnSendMessage = customtkinter.CTkButton(master=self.messageEnterFrame, text="", command=lambda: self.sendMessage(), fg_color="transparent", 
                                                         hover='#242424')
        self.btnSendMessage.place(relx=0.95, rely=0.5, relwidth = 0.075, relheight = 0.5, anchor=customtkinter.CENTER)
        
        self.icon = customtkinter.CTkImage(
                       dark_image=Image.open("sendMsgIcon.png"),
                       size=(36, 36))

        self.btnSendMessage.configure(image=self.icon)
        
        self.messageListFrame = customtkinter.CTkScrollableFrame(master=self)
        self.messageListFrame.place(relx=0.5, rely=0.44, relwidth=0.98, relheight=0.86, anchor="center")

        for msg in msgs:
            create_bubble(self.messageListFrame, controller, msg['text'], msg['senderName'], msg['messageTime'], msg['side'])

    def sendMessage(self):
        print("sending msg!!")
        
class ChattingFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        chatListFrame = Chatting_ChatListFrame(self, controller)
        usernameFrame = Chatting_UsernameFrame(self, controller)
        signoutFrame = Chatting_SignOutFrame(self, controller)
        msgListFrame = Chatting_MessageListFrame(self, controller)

        usernameFrame.place(relx=0.15, rely=0.075, relwidth=0.3, relheight=0.15, anchor="center")
        chatListFrame.place(relx=0.15, rely=0.525, relwidth=0.3, relheight=0.75, anchor="center")
        signoutFrame.place(relx=0.15, rely=0.95, relwidth=0.3, relheight=0.1, anchor="center")
        msgListFrame.place(relx=0.65, rely=0.5, relwidth=0.7, relheight=1, anchor="center")

# thread = threading.Thread(target=backgroundFunc, daemon=True)
# thread.start()

app = ChatUI()
app.mainloop()
