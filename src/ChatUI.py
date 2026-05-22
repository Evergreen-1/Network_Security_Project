# Main Menu
import customtkinter
from CTkToolTip import *
from PIL import Image

RESOURCE_FOLDER = "res/"

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme(RESOURCE_FOLDER + "FlaresOfTheBlazingSun.json")

def defaultButton():
    print("button pressed")

class ChatUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.headingFont = ("Roboto", 24)
        self.msgNameFont = ("Roboto", 18, "bold")
        self.msgTimeFont = ("Roboto", 12)
        self.textColour = '#FEA943'

        self.msgs = (  {"text": "Let's begin. The first decision: A story about a baby bird", "senderName":"Not You", "messageTime" :"00:00", "side":"left"},
        {"text": "This story happened when Robin and I were very young. We were victims of the Stellaron Disaster, and The Family's Mr. Gopher Wood — who would later become the Dreammaster of Penacony — saw that we siblings had no one to turn to and took us in.", "senderName":"Not You", "messageTime": "00:00", "side":"left"},
        {"text" : "Let's begin. The first decision: A story about a baby bird", "senderName": "Not You", "messageTime" : "00:00", "side":"left"},
        {"text" : "Nurture with care in a cage", "senderName": "You", "messageTime" : "00:00", "side":"right"},
        {"text" : "Why do birds fly? They fly because they want to. Even if they don't have a reason. Even if there wings break and they might die. They don't fly for others or because they've been ordered by anyone. They just feel 'I want to fly', and take to the skies on their own. That is my answer. That is who I am.", "senderName": "You", "messageTime" : "00:00", "side":"right"},
        {"text" : "Star Platinum, Za Warudo!!!!", "senderName": "You", "messageTime" : "00:00", "side":"right"}
)

        self.chats = ("chat1", "chat2", "chat3")
        self.channels = ("channel1", "channel2", "channel3", "channel4", "channel5")
        self.users = ("user1", "user2", "user3", "user4", "user5","user6", "user7", "user8", "user9", "user10")
        
        self.frames = {}
        self.username = "DefaultNameText"
        self.transport = "Cleartext"

        for F in (MainMenuFrame, ChattingFrame, SignInFrame, ChangeUsernameFrame, ChannelDetailsFrame, UserDetailsFrame, NewChannelFrame):
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
            case "SignInFrame":
                print("moving to Sign in frame")
                windowWidth = 400
                windowHeight = 180
                screenWidth = self.winfo_screenwidth()
                screenHeight = self.winfo_screenheight()
                scalingFactor = customtkinter.ScalingTracker.get_window_scaling(self)
                x = int(((screenWidth / 2) - (windowWidth / 2)) * scalingFactor)
                y = int(((screenHeight / 2) - (windowHeight / 2)) * scalingFactor)
                self.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
                self.minsize(windowWidth, windowHeight)
            case "ChangeUsernameFrame":
                print("moving to Change Username Frame")
                windowWidth = 400
                windowHeight = 180
                screenWidth = self.winfo_screenwidth()
                screenHeight = self.winfo_screenheight()
                scalingFactor = customtkinter.ScalingTracker.get_window_scaling(self)
                x = int(((screenWidth / 2) - (windowWidth / 2)) * scalingFactor)
                y = int(((screenHeight / 2) - (windowHeight / 2)) * scalingFactor)
                self.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
                self.minsize(windowWidth, windowHeight)
            case "ChannelDetailsFrame":
                print("moving to Channel Details frame")
                windowWidth = 400
                windowHeight = 200
                screenWidth = self.winfo_screenwidth()
                screenHeight = self.winfo_screenheight()
                scalingFactor = customtkinter.ScalingTracker.get_window_scaling(self)
                x = int(((screenWidth / 2) - (windowWidth / 2)) * scalingFactor)
                y = int(((screenHeight / 2) - (windowHeight / 2)) * scalingFactor)
                self.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
                self.minsize(windowWidth, windowHeight)
            case "UserDetailsFrame":
                print("moving to User Details frame")
                windowWidth = 400
                windowHeight = 200
                screenWidth = self.winfo_screenwidth()
                screenHeight = self.winfo_screenheight()
                scalingFactor = customtkinter.ScalingTracker.get_window_scaling(self)
                x = int(((screenWidth / 2) - (windowWidth / 2)) * scalingFactor)
                y = int(((screenHeight / 2) - (windowHeight / 2)) * scalingFactor)
                self.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
                self.minsize(windowWidth, windowHeight)
            case "NewChannelFrame":
                print("moving to Create Channel frame")
                windowWidth = 400
                windowHeight = 200
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
        
        self.controller = controller
        
        self.lblTitle = customtkinter.CTkLabel(self, text="NEXXXXXAAAA!!!", font=controller.headingFont, text_color=controller.textColour)
        self.lblTitle.place(relx=0.5, rely=0.15, relwidth=0.5, anchor=customtkinter.CENTER)
        
        self.clearTextChat = customtkinter.CTkButton(self, text="Cleartext Chat", command=lambda: self.JoinCleartextChat())
        self.clearTextChat.place(relx=0.5, rely=0.35, relwidth=0.5, anchor=customtkinter.CENTER)

        self.encryptedChat = customtkinter.CTkButton(self, text="Encrypted Chat", command=lambda: self.JoinEncryptedChat())
        self.encryptedChat.place(relx=0.5, rely=0.5, relwidth=0.5, anchor=customtkinter.CENTER)

        self.extendedEncryptionChat = customtkinter.CTkButton(self, text="Extended Encryption Chat", command=lambda: self.JoinExtendedEncryptionChat())
        self.extendedEncryptionChat.place(relx=0.5, rely=0.65, relwidth=0.5, anchor=customtkinter.CENTER)
        
        self.buttonExitChattingApp = customtkinter.CTkButton(self, text="EXIT", command=lambda: controller.exitChattingApp())
        self.buttonExitChattingApp.place(relx=0.5, rely=0.8, relwidth=0.5, anchor=customtkinter.CENTER)

    def JoinCleartextChat(self):
    	print("joining cleartext!")
    	self.controller.changeFrame("ChattingFrame")
    
    def JoinEncryptedChat(self):
    	print("joining cleartext!")
    	self.controller.changeFrame("SignInFrame")
    
    def JoinExtendedEncryptionChat(self):
    	print("joining cleartext!")
    	self.controller.changeFrame("SignInFrame")

        
class Chatting_UsernameFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.btnChangeUsername = customtkinter.CTkButton(master=self, text="", command=lambda: self.changeUsernameFunc(), fg_color="#242424", 
                                                         hover='#242424')
        self.btnChangeUsername.place(relx=0.9, rely=0.7, relwidth = 0.15, relheight = 0.35, anchor=customtkinter.CENTER)
        
        self.icon = customtkinter.CTkImage(
                       dark_image=Image.open(RESOURCE_FOLDER + "editIcon.png"),
                       size=(36, 36))

        self.btnChangeUsername.configure(image=self.icon)
        
        self.lblTitle = customtkinter.CTkLabel(self, text=controller.username, font=controller.headingFont, text_color=controller.textColour)
        self.lblTitle.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
    
    def changeUsernameFunc(self):
        print("Changing username")
        self.controller.changeFrame("ChangeUsernameFrame")
        

class Chatting_ChatListFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.chatList = customtkinter.CTkScrollableFrame(master=self)
        self.chatList.place(relx=0.5, rely=0.55, relwidth=1, relheight=0.9, anchor="center")

        self.segbtnChatType = customtkinter.CTkSegmentedButton(master=self,
                                                     values=["My Chats", "Available Channels", "Online Users"],
                                                     command=self.selectChatType)
        self.segbtnChatType.place(relx=0.5, rely=0.05, relwidth = 1, relheight = 0.1, anchor=customtkinter.CENTER)
        self.segbtnChatType.set("My Chats")  # set initial value
        self.selectChatType("My Chats")  # set initial value

    def openChat(self, chatName):
        print("openChat: ", chatName)
        #reload msglist? 
    
    def showChannelDetails(self, channelName):
        print("show channel details for channel: ", channelName)
        self.controller.changeFrame("ChannelDetailsFrame")
    
    def showUserDetails(self, username):
        print("username: ", username)
        self.controller.changeFrame("UserDetailsFrame")
    
    def createNewChannel(self):
        print("creating a new channel!")
        self.controller.changeFrame("NewChannelFrame")    
    
    def selectChatType(self, value):
        print("chat type button clicked:", value)
        
        
        for chatType in self.chatList.winfo_children():
            chatType.destroy()
        
        match value:
            case "My Chats":
                for chat in self.controller.chats:
            	    newChat = customtkinter.CTkFrame(master=self.chatList)
            	    
            	    btnchatName = customtkinter.CTkButton(newChat, text=chat, font= self.controller.msgNameFont, command=lambda chat=chat: self.openChat(chat))
            	    btnchatName.pack(anchor="center", fill='x', expand=True)
            	    
            	    newChat.pack(anchor='center', padx=1, pady=3, fill='x', expand=True)
            case "Available Channels":
            
                newChat = customtkinter.CTkFrame(master=self.chatList)
            	    
                btnchatName = customtkinter.CTkButton(newChat, text="+Create Channel", font= self.controller.msgNameFont, command=lambda : self.createNewChannel())
                btnchatName.pack(anchor="center", fill='x', expand=True)
            	    
                newChat.pack(anchor='center', padx=1, pady=3, fill='x', expand=True)
            
                for channel in self.controller.channels:
            	    newChat = customtkinter.CTkFrame(master=self.chatList)
            	    
            	    btnchatName = customtkinter.CTkButton(newChat, text=channel, font= self.controller.msgNameFont, command=lambda channel=channel: self.showChannelDetails(channel))
            	    btnchatName.pack(anchor="center", fill='x', expand=True)
            	    
            	    newChat.pack(anchor='center', padx=1, pady=3, fill='x', expand=True)
            case "Online Users":
                for user in self.controller.users:
            	    newChat = customtkinter.CTkFrame(master=self.chatList)
            	    
            	    btnchatName = customtkinter.CTkButton(newChat, text=user, font= self.controller.msgNameFont, command=lambda user=user: self.showUserDetails(user))
            	    btnchatName.pack(anchor="center", fill='x', expand=True)
            	    
            	    newChat.pack(anchor='center', padx=1, pady=3, fill='x', expand=True)
            case _:
                print("Error!!! invalid option selected for chat type. option:", value)

class Chatting_SignOutFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.btnSignOut = customtkinter.CTkButton(self, text="Sign Out", command=lambda: controller.changeFrame("MainMenuFrame"))
        self.btnSignOut.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

def create_bubble(master, controller, text, senderName="You", messageTime="00:00", side="left", showName = True):
    # Determine colors based on sender
    fg_color = ("#f08315", "#f08315") if side == "right" else ("#ebebeb", "#f16146")
    text_color = ("black", "white")
    anchor = "e" if side == "right" else "w"
    othranchor = "w" if side == "right" else "e"
    msgFrame = customtkinter.CTkFrame(master, fg_color='transparent', border_width=0)
    
    
    padYVal = 5
    
    if showName:
        lblsenderName = customtkinter.CTkLabel(msgFrame, text=senderName, font=controller.msgNameFont, text_color=controller.textColour)
        lblsenderName.pack(anchor=anchor, pady=0, padx=0)
        padYVal = 0
    
    bubble = customtkinter.CTkLabel(
        msgFrame,
        text=text, 
        corner_radius=15, 
        fg_color=fg_color,
        text_color=text_color,
        padx=10,
        pady=padYVal,
        wraplength=500 # Ensures text wraps in the bubble
    )
    bubble.pack(anchor=anchor, pady=0, padx=0)
    bubbleWidth = bubble.winfo_width()
    lblmsgTime = customtkinter.CTkLabel(msgFrame, text=messageTime, font=controller.msgTimeFont, text_color=controller.textColour)
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
                       dark_image=Image.open(RESOURCE_FOLDER + "sendMsgIcon.png"),
                       size=(36, 36))

        self.btnSendMessage.configure(image=self.icon)
        
        self.messageListFrame = customtkinter.CTkScrollableFrame(master=self)
        self.messageListFrame.place(relx=0.5, rely=0.44, relwidth=0.98, relheight=0.86, anchor="center")

        lastSender = ""

        for msg in controller.msgs:
            if lastSender == msg['senderName']:
                create_bubble(self.messageListFrame, controller, msg['text'], msg['senderName'], msg['messageTime'], msg['side'], False)
            else:
                create_bubble(self.messageListFrame, controller, msg['text'], msg['senderName'], msg['messageTime'], msg['side'], True)
            lastSender = msg['senderName']

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

class SignInFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.entryPrivateKey = customtkinter.CTkEntry(master=self, placeholder_text="Enter your private key here.")
        self.entryPrivateKey.place(relx=0.5, rely=0.25, relwidth=0.7, relheight=0.25, anchor="center")

        self.btnSignIn = customtkinter.CTkButton(self, text="Sign In", command=lambda: self.signIn())
        self.btnSignIn.place(relx=0.25, rely=0.75, relwidth=0.45, relheight=0.3, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("MainMenuFrame"))
        self.btnCancel.place(relx=0.75, rely=0.75, relwidth=0.45, relheight=0.3, anchor=customtkinter.CENTER)

    def signIn(self):
        print("Signing in!", self.entryPrivateKey.get())
        self.controller.changeFrame("ChattingFrame")   

class ChangeUsernameFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.entryUsername = customtkinter.CTkEntry(master=self, placeholder_text="Enter your new username here.")
        self.entryUsername.place(relx=0.5, rely=0.25, relwidth=0.7, relheight=0.25, anchor="center")

        self.userNameToolTip = CTkToolTip(self.entryUsername, message="Username must be unique\nCleartext user's names will auomatically be padded with \'clear-\'\nUsernames cannot contain \':\'\n Usernames are limited to 20 chars total")

        self.btnChangeUsername = customtkinter.CTkButton(self, text="Confirm Name", command=lambda: self.changeUsername())
        self.btnChangeUsername.place(relx=0.25, rely=0.75, relwidth=0.45, relheight=0.3, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("ChattingFrame"))
        self.btnCancel.place(relx=0.75, rely=0.75, relwidth=0.45, relheight=0.3, anchor=customtkinter.CENTER)

    def changeUsername(self):
        print("Changing username!", self.entryUsername.get())
        username = self.entryUsername.get().strip()
        username = username.replace(":", "")
        if self.controller.transport == "Cleartext":
            username = "clear-" + username
        length = len(username)
        if (length > 20):
            length = 20
        username = username[0:length]
        
        print("Formatted username:", username)
        
        self.controller.changeFrame("ChattingFrame")

class ChannelDetailsFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.channelDetails = customtkinter.CTkTextbox(master=self)
        self.channelDetails.insert("0.0", ("channel Details here!!!"))
        self.channelDetails.place(relx=0.5, rely=0.35, relwidth=0.7, relheight=0.67, anchor="center")

	self.Joined = False

	# TODO check if we're in the channel already

	if self.Joined:
	    self.btnJoinChannel = customtkinter.CTkButton(self, text="Join Channel", command=lambda: self.JoinChannel())
            self.btnJoinChannel.place(relx=0.255, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)
        else:
            self.btnLeaveChannel = customtkinter.CTkButton(self, text="Leave Channel", command=lambda: self.LeaveChannel())
            self.btnLeaveChannel.place(relx=0.255, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("ChattingFrame"))
        self.btnCancel.place(relx=0.745, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)

    def JoinChannel(self):
        print("Joining Channel!!")
        self.controller.changeFrame("ChattingFrame")
    
    def LeaveChannel(self):
        print("Leaving Channel!!")
        self.controller.changeFrame("ChattingFrame")

class NewChannelFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.entryChannelName = customtkinter.CTkEntry(master=self, placeholder_text="Enter new channel name here.")
        self.entryChannelName.place(relx=0.5, rely=0.125, relwidth=0.7, relheight=0.2, anchor="center")

        self.channelNameToolTip = CTkToolTip(self.entryChannelName, message="Channel name can only contain letters, numbers, underscores and dashes and is limited to 20 chars.\nEach user can create atmost 20 channels at a time.\n Any excess will be trimmed.")
        
        self.entryChannelDesc = customtkinter.CTkTextbox(master=self)
        self.entryChannelDesc.insert("0.0", "Enter new channel decription here.")
        self.entryChannelDesc.place(relx=0.5, rely=0.45, relwidth=0.7, relheight=0.4, anchor="center")

        self.channelNameToolTip = CTkToolTip(self.entryChannelDesc, message="Channel description is limited to 100 chars.\n Any excess will be trimmed.")

        self.btnCreateChannel = customtkinter.CTkButton(self, text="Create Channel", command=lambda: self.CreateChannel())
        self.btnCreateChannel.place(relx=0.255, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("ChattingFrame"))
        self.btnCancel.place(relx=0.745, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)

    def CreateChannel(self):
        print("Created Channel!!")
        self.controller.changeFrame("ChattingFrame")

class UserDetailsFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.userDetails = customtkinter.CTkTextbox(master=self)
        self.userDetails.insert("0.0", ("user Details here!!!"))
        self.userDetails.place(relx=0.5, rely=0.35, relwidth=0.7, relheight=0.67, anchor="center")

        self.btnMsgUser = customtkinter.CTkButton(self, text="Join Channel", command=lambda: self.MsgUser())
        self.btnMsgUser.place(relx=0.25, rely=0.85, relwidth=0.45, relheight=0.27, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("ChattingFrame"))
        self.btnCancel.place(relx=0.75, rely=0.85, relwidth=0.45, relheight=0.27, anchor=customtkinter.CENTER)

    def MsgUser(self):
        print("Start chat with user!!")
        self.controller.changeFrame("ChattingFrame")


if "__main__" == __name__:
    app = ChatUI()
    app.mainloop()
