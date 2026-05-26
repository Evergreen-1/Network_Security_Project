# Main Menu
import asyncio
import base64
import customtkinter
from CTkToolTip import *
from PIL import Image
from async_tkinter_loop.mixins import AsyncCTk
from async_tkinter_loop import async_handler
from datetime import datetime
from src import EventHandler
from src.networkProtocols.CleartextProtocol import CleartextProtocol
from src.networkProtocols.EncryptionProtocol import EncryptionProtocol
from src.networkProtocols.ExtendedEncryptionProtocol import ExtendedEncryptionProtocol
from src.ChatProtocol import ChatProtocol
from src.ChatClient import ChatClient
from src.networkProtocols.Encryption import Encryption
from src.networkProtocols.Encryption import ExtendedEncryption

RESOURCE_FOLDER = "res/"

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme(RESOURCE_FOLDER + "FlaresOfTheBlazingSun.json")

def create_bubble(master, controller, text, senderName="You", messageTime="00:00", side="left", showName = True):
    # Determine colors based on sender
    fg_color = ("#f08315", "#f08315") if side == "right" else ("#ebebeb", "#f16146")
    text_color = ("black", "white")
    anchor = "e" if side == "right" else "w"
    othranchor = "w" if side == "right" else "e"
    
    if side == "middle":
       anchor = "center"
       fg_color = ("#333333", "#242424")
    
    msgFrame = customtkinter.CTkFrame(master, fg_color='transparent', border_width=0)
    
    padYVal = 5
    
    if side == "middle":
        bubbleFrame = customtkinter.CTkFrame(msgFrame, fg_color='transparent', border_width=0)
    
        bubble = customtkinter.CTkLabel(
        bubbleFrame,
        text=text, 
        corner_radius=15, 
        fg_color=fg_color,
        text_color=text_color,
        padx=0,
        pady=padYVal,
        wraplength=500 # Ensures text wraps in the bubble
        )
        bubble.pack(anchor=anchor, pady=0, padx=0)
        bubbleFrame.pack(anchor=anchor, pady=0, padx=0)
        msgFrame.pack(anchor=anchor, pady=0, padx=10)
        return msgFrame
    
    if showName:
        lblsenderName = customtkinter.CTkLabel(msgFrame, text=senderName, font=controller.msgNameFont, text_color=controller.textColour)
        lblsenderName.pack(anchor=anchor, pady=0, padx=0)
        padYVal = 0
    
    bubbleFrame = customtkinter.CTkFrame(msgFrame, fg_color='transparent', border_width=0)
    
    bubble = customtkinter.CTkLabel(
        bubbleFrame,
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
    lblmsgTime = customtkinter.CTkLabel(bubbleFrame, text=messageTime, font=controller.msgTimeFont, text_color=controller.textColour)
    lblmsgTime.pack(anchor=othranchor, pady=0, padx=10)
    #lblmsgTime.pack(anchor=anchor, padx=(bubbleWidth, 0))
    bubbleFrame.pack(anchor=anchor, pady=0, padx=0)
    msgFrame.pack(anchor=anchor, pady=0, padx=10)
    return msgFrame

def showChat(master, controller, messageList : list):
    # message list contains [(sender), (timesent),(mesageText)]    
    for chatType in master.winfo_children():
        chatType.destroy()
    
    lastSender = ""

    for msg in messageList:
        side = "left"
        if msg["sender"] == controller.transportProtocolInUse.username:
            side = "right"
        if msg["sender"] == "":
            side = "middle"
        print("side is: ", side)
        if lastSender == msg['sender']:
            create_bubble(master, controller, msg['text'], msg['sender'], msg['time'], side, False)
        else:
            create_bubble(master, controller, msg['text'], msg['sender'], msg['time'], side, True)
        lastSender = msg['sender']
    
    master.update_idletasks()
    master._parent_canvas.yview_moveto(0.0)    
    master.update_idletasks()
    master._parent_canvas.yview_moveto(1.0)

class ChatUI(customtkinter.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()

        self.headingFont = ("Roboto", 24)
        self.msgNameFont = ("Roboto", 18, "bold")
        self.msgTimeFont = ("Roboto", 12)
        self.textColour = '#FEA943'
		        
        self.transportProtocolInUse = None

        self.channelMessages = [] # dict of chats - channelName/user: [(msg1), (msg2), (msg3)] 
        self.userMessages = []
	#[channelName/user, [(msg1), (msg2), (msg3)]]
	
        self.chatsWithUsers = []
        self.chatsWithChannels = []
        self.channels = []
        self.users = []
        
        self.eventHandler = EventHandler.Handler(self, showChat)
        
        self.showChannel = False # if false, show user instead
        self.currentChat = None
        
        self.isCleartext = False
        
        self.frames = {}

        for F in (MainMenuFrame, ChattingFrame, SignInFrame, ChangeUsernameFrame, ChannelDetailsFrame, UserDetailsFrame, NewChannelFrame):
            frameName = F.__name__
            frame = F(parent=self, controller=self)
            frame.place(relx=0.5, rely=0.5, relwidth=0.99, relheight=0.99, anchor="center")
            self.frames[frameName] = frame
            
        self.currentFrame = "MainMenuFrame"
        self.frames[self.currentFrame].pack(fill="both", expand=True)
        self.changeFrame(self.currentFrame)
        
        self.protocol("WM_DELETE_WINDOW", self.exitChattingApp)
    
    async def updateUsers(self):
       while self.transportProtocolInUse:
          self.users = await self.transportProtocolInUse.list_users()
          print("Found list of users: ", self.users)
          
          if self.frames["ChattingFrame"].chatListFrame.segbtnChatType.get()=="Online Users":
              self.frames["ChattingFrame"].chatListFrame.selectChatType("Online Users")
          
          #for user in self.users:
          #    if (not (user in newUsersList)):
          #        i = 0
          #        while (userMessages[i][0] != user):
          #            i += 1
          #        usermessages.pop(i)
          await asyncio.sleep(60)
    
    async def updateChannels(self):
       while self.transportProtocolInUse:
          self.channels = await self.transportProtocolInUse.list_channels()
          print("Found list of channels: ", self.channels)
          
          if self.frames["ChattingFrame"].chatListFrame.segbtnChatType.get()=="Available Channels":
              self.frames["ChattingFrame"].chatListFrame.selectChatType("Available Channels")
          
          await asyncio.sleep(60)
    
    def changeFrame(self, frameName):
        
        if self.currentFrame in self.frames:
           self.frames[self.currentFrame].pack_forget()
        
        self.currentFrame = frameName
        
        frame = self.frames[self.currentFrame]
        frame.pack(fill= "both", expand = True)
        frame.tkraise()
        
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

    @async_handler            
    async def exitChattingApp(self):
        if self.transportProtocolInUse:
            self.updateUsersTask.cancel()
            try:
                await self.updateUsersTask
            except asyncio.CancelledError:
                pass
            self.updateChannelsTask.cancel()
            try:
                await self.updateChannelsTask
            except asyncio.CancelledError:
                pass
            #try:
            #    await asyncio.gather(self.updateUsersTask, self.updateChannelsTask, return_exceptions=True)
            #except asyncio.CancelledError:
            #    pass
            await self.transportProtocolInUse.disconnect()
        self.destroy()

class MainMenuFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.controller = controller
        
        self.lblTitle = customtkinter.CTkLabel(self, text="Cinder", font=controller.headingFont, text_color=controller.textColour)
        self.lblTitle.place(relx=0.5, rely=0.15, relwidth=0.5, anchor=customtkinter.CENTER)
        
        self.clearTextChat = customtkinter.CTkButton(self, text="Cleartext Chat", command=lambda: self.JoinCleartextChat())
        self.clearTextChat.place(relx=0.5, rely=0.35, relwidth=0.5, anchor=customtkinter.CENTER)

        self.encryptedChat = customtkinter.CTkButton(self, text="Encrypted Chat", command=lambda: self.JoinEncryptedChat())
        self.encryptedChat.place(relx=0.5, rely=0.5, relwidth=0.5, anchor=customtkinter.CENTER)

        self.extendedEncryptionChat = customtkinter.CTkButton(self, text="Extended Encryption Chat", command=lambda: self.JoinExtendedEncryptionChat())
        self.extendedEncryptionChat.place(relx=0.5, rely=0.65, relwidth=0.5, anchor=customtkinter.CENTER)
        
        self.buttonExitChattingApp = customtkinter.CTkButton(self, text="EXIT", command=lambda: controller.exitChattingApp())
        self.buttonExitChattingApp.place(relx=0.5, rely=0.8, relwidth=0.5, anchor=customtkinter.CENTER)

    @async_handler
    async def JoinCleartextChat(self):
    	print("Joining chat as cleartext user!")
    	self.controller.transportProtocolInUse = ChatClient(ChatProtocol(CleartextProtocol()))
    	self.controller.transportProtocolInUse.on_event = self.controller.eventHandler.handleEvent
    	message = await self.controller.transportProtocolInUse.connect()
    	
    	#print(message)
    	msgTime = datetime.now().strftime("%H:%M:%S")
    	
    	self.controller.chatsWithUsers.clear()
    	self.controller.chatsWithChannels.clear()
    	self.controller.chatsWithChannels.append("Server")
    	self.controller.channelMessages.clear()
    	self.controller.channelMessages.append(("Server", [{"sender":"Server", "text": message, "time":msgTime}]))
    	self.controller.userMessages.clear()
    	
    	self.controller.currentChat = "Server"
    	self.controller.showChannel = False
    	
    	self.controller.isCleartext = True
    	
    	#print(self.controller.messages[0])
    	self.controller.frames["ChattingFrame"].msgListFrame.chatName.configure(text="Server")
    	showChat(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[0][1])
    	#print(self.controller.transportProtocolInUse.username)
    	
    	self.controller.updateUsersTask = asyncio.create_task(self.controller.updateUsers())
    	self.controller.updateChannelsTask = asyncio.create_task(self.controller.updateChannels())
    	
    	self.controller.frames["ChattingFrame"].chatListFrame.selectChatType("My Chats")
    	self.controller.frames["ChattingFrame"].chatListFrame.openChannel("Server")
    	self.controller.frames["ChattingFrame"].usernameFrame.lblUsername.configure(text = self.controller.transportProtocolInUse.username)	
    	self.controller.changeFrame("ChattingFrame")
    
    @async_handler
    async def JoinEncryptedChat(self):
    	print("Joining Encryption!")
    	self.controller.frames["SignInFrame"].ExtendedTransport = False 
    	self.controller.changeFrame("SignInFrame")
    	
    def JoinExtendedEncryptionChat(self):
    	print("Joining Extended Enctyption!")
    	self.controller.frames["SignInFrame"].ExtendedTransport = True
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
        
        self.lblUsername = customtkinter.CTkLabel(self, text="", font=controller.headingFont, text_color=controller.textColour)
        self.lblUsername.place(relx=0.5, rely=0.4, anchor=customtkinter.CENTER)
    
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
        messages = []
        i = 0
        while (self.controller.userMessages[i][0] != chatName):
            i += 1
        messages = self.controller.userMessages[i][1]
        #print(messages)
        
        self.controller.currentChat = chatName
        self.controller.showChannel = False
        
        self.controller.frames["ChattingFrame"].msgListFrame.sendMessageToolTip.hide()
        self.controller.frames["ChattingFrame"].msgListFrame.msgBox.configure(state="normal")
        self.controller.frames["ChattingFrame"].msgListFrame.chatName.configure(text=chatName)
        showChat(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.userMessages[i][1]) 
    
    def openChannel(self, channel):
        print("openChannel: ", channel)
        messages = []
        i = 0
        while (self.controller.channelMessages[i][0] != channel):
            i += 1
        messages = self.controller.channelMessages[i][1]
        #print(messages)
        
        self.controller.currentChat = channel
        self.controller.showChannel = True
        
        if channel == "Server":
            self.controller.frames["ChattingFrame"].msgListFrame.sendMessageToolTip.show()
            self.controller.frames["ChattingFrame"].msgListFrame.msgBox.configure(state="disabled")
        else:
            self.controller.frames["ChattingFrame"].msgListFrame.sendMessageToolTip.hide()
            self.controller.frames["ChattingFrame"].msgListFrame.msgBox.configure(state="normal")
        
        self.controller.frames["ChattingFrame"].msgListFrame.chatName.configure(text=channel)
        showChat(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[i][1])
    
    @async_handler
    async def showChannelDetails(self, channelName):
        print("show channel details for channel: ", channelName)
        
        channelDetails = await self.controller.transportProtocolInUse.channel_info(channelName)
        print(channelDetails)
        
        users = ""
        for user in channelDetails["members"]:
           users += user + ", "
        users = users[0:-2]
        
        channelDetailsText = "Name: " + channelDetails["channel"] + "\nDescription: " + channelDetails["description"] + "\nMembers: " + users  
        
        self.controller.frames["ChannelDetailsFrame"].channelDetails.configure(state="normal")
        self.controller.frames["ChannelDetailsFrame"].channelDetails.delete("1.0", "end")
        self.controller.frames["ChannelDetailsFrame"].channelDetails.insert("0.0", channelDetailsText)
        self.controller.frames["ChannelDetailsFrame"].channelDetails.configure(state="disabled")
        self.controller.frames["ChannelDetailsFrame"].channel = channelDetails["channel"]
        
        if channelDetails["channel"] in self.controller.chatsWithChannels:
            self.controller.frames["ChannelDetailsFrame"].btnJoinOrLeaveChannel.configure(text = "Leave Channel", command=self.controller.frames["ChannelDetailsFrame"].LeaveChannel)
        else:
            self.controller.frames["ChannelDetailsFrame"].btnJoinOrLeaveChannel.configure(text = "Join Channel", command=self.controller.frames["ChannelDetailsFrame"].JoinChannel)
        
        self.controller.changeFrame("ChannelDetailsFrame")
    
    @async_handler
    async def showUserDetails(self, username):
        print("Showing user details for ", username)
        
        userDetails = await self.controller.transportProtocolInUse.whois(username)
        #print(userDetails)
        
        channels = ""
        for channel in userDetails["channels"]:
           channels += channel + ", "
        channels = channels[0:-2]
        
        userDetailText = "Username: " + userDetails["username"] + "\nChannels: " + channels + "\nTransport: " + userDetails["transport"] + "\nPublic Key: " + str(userDetails["wireguard_public_key"])  
        
        self.controller.frames["UserDetailsFrame"].transport = userDetails["transport"]
        self.controller.frames["UserDetailsFrame"].username = userDetails["username"]
        self.controller.frames["UserDetailsFrame"].userDetails.configure(state="normal")
        self.controller.frames["UserDetailsFrame"].userDetails.delete("1.0", "end")
        self.controller.frames["UserDetailsFrame"].userDetails.insert("0.0", userDetailText)
        self.controller.frames["UserDetailsFrame"].userDetails.configure(state="disabled")
        self.controller.changeFrame("UserDetailsFrame")
    
    def createNewChannel(self):
        print("creating a new channel!")
        self.controller.changeFrame("NewChannelFrame")    
    
    def selectChatType(self, value):
        
        print("chat type button clicked:", value)
        self.segbtnChatType.set(value)
        
        for chatType in self.chatList.winfo_children():
            chatType.destroy()
        match value:
            case "My Chats":
                for chat in self.controller.chatsWithChannels:
            	    newChat = customtkinter.CTkFrame(master=self.chatList)
            	    
            	    btnchatName = customtkinter.CTkButton(newChat, text=chat, font= self.controller.msgNameFont, command=lambda chat=chat: self.openChannel(chat))
            	    btnchatName.pack(anchor="center", fill='x', expand=True)
            	    
            	    newChat.pack(anchor='center', padx=1, pady=3, fill='x', expand=True)
                for chat in self.controller.chatsWithUsers:
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
            	    
            	    btnchatName = customtkinter.CTkButton(newChat, text=(channel + (20-len(channel))*" " + "\t±"), font= self.controller.msgNameFont, command=lambda channel=channel: self.showChannelDetails(channel), anchor = "w")
            	    btnchatName.pack(anchor="center", fill='x', expand=True)
            	    
            	    newChat.pack(anchor='center', padx=1, pady=3, fill='x', expand=True)
            case "Online Users":
                for user in self.controller.users:
                    if user != self.controller.transportProtocolInUse.username:
            	        newChat = customtkinter.CTkFrame(master=self.chatList)
            	    
            	        btnchatName = customtkinter.CTkButton(newChat, text=user, font= self.controller.msgNameFont, command=lambda user=user: self.showUserDetails(user))
            	        btnchatName.pack(anchor="center", fill='x', expand=True)
            	    
            	        newChat.pack(anchor='center', padx=1, pady=3, fill='x', expand=True)
            case _:
                print("Error!!! invalid option selected for chat type. option:", value)

class Chatting_SignOutFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
	
        self.controller = controller

        self.btnSignOut = customtkinter.CTkButton(self, text="Sign Out", command=self.signOut)
        self.btnSignOut.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
    
    @async_handler
    async def signOut(self):
        
        self.channelMessages = [] # dict of chats - channelName/user: [(msg1), (msg2), (msg3)] 
        self.userMessages = []
	#[channelName/user, [(msg1), (msg2), (msg3)]]
        
        self.controller.isCleartext = False
        self.chatsWithUsers = []
        self.chatsWithChannels = []
        self.channels = []
        self.users = []	
        
        if self.controller.transportProtocolInUse:
            self.controller.updateUsersTask.cancel()
            try:
                await self.controller.updateUsersTask
            except asyncio.CancelledError:
                pass
            self.controller.updateChannelsTask.cancel()
            try:
                await self.controller.updateChannelsTask
            except asyncio.CancelledError:
                pass
            await self.controller.transportProtocolInUse.disconnect()
            self.controller.transportProtocolInUse = None
        self.controller.changeFrame("MainMenuFrame")

class Chatting_MessageListFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.chatName = customtkinter.CTkLabel(self, text="ChannelName", font=controller.headingFont, text_color=controller.textColour)
        self.chatName.place(relx=0.125, rely=0.06, relheight=0.08, anchor=customtkinter.CENTER)

        self.messageEnterFrame = customtkinter.CTkFrame(master=self)
        self.messageEnterFrame.place(relx=0.5, rely=0.93, relwidth=0.95, relheight=0.1, anchor="center")

        self.msgBox = customtkinter.CTkEntry(master=self.messageEnterFrame, placeholder_text="Enter your message here.")
        self.msgBox.place(relx=0.45, rely=0.5, relwidth=0.88, relheight=0.8, anchor="center")
        self.msgBox.bind("<Return>", self.onEnterPressed)

        self.btnSendMessage = customtkinter.CTkButton(master=self.messageEnterFrame, text="", command=lambda: self.sendMessage(), fg_color="transparent", 
                                                         hover='#242424')
        self.btnSendMessage.place(relx=0.95, rely=0.5, relwidth = 0.075, relheight = 0.5, anchor=customtkinter.CENTER)
        
        self.icon = customtkinter.CTkImage(
                       dark_image=Image.open(RESOURCE_FOLDER + "sendMsgIcon.png"),
                       size=(36, 36))

        self.btnSendMessage.configure(image=self.icon)
        
        self.sendMessageToolTip = CTkToolTip(self.msgBox, message="Cannot send messages to Server")
        
        self.messageListFrame = customtkinter.CTkScrollableFrame(master=self)
        self.messageListFrame.place(relx=0.5, rely=0.49, relwidth=0.98, relheight=0.75, anchor="center")

    
    def onEnterPressed(self, event):
        self.sendMessage()

    @async_handler
    async def sendMessage(self):
        print("sending msg!!")
        
        msgText = self.msgBox.get()
        self.msgBox.delete(0, "end")
        if len(msgText)<=0:
            return
        msgTime = datetime.now().strftime("%H:%M:%S")
        if (not((self.controller.currentChat == "Server") and (self.controller.showChannel == True))):            
            if self.controller.showChannel:
                try:
                    await self.controller.transportProtocolInUse.message_channel(self.controller.currentChat, msgText)
                    i = 0
                    while self.controller.channelMessages[i][0] != self.controller.currentChat:
                        i+=1
                    self.controller.channelMessages[i][1].append({"sender": self.controller.transportProtocolInUse.username, "text": msgText, "time":msgTime})
                    self.controller.frames["ChattingFrame"].msgListFrame.chatName.configure(text=self.controller.currentChat)
                    showChat(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[i][1])
                except Exception as e:
                    print("Error:", e)
                    if str(e) != "User not found":
                        return
                    i = 0
                    while self.controller.channelMessages[i][0] != self.controller.currentChat:
                        i+=1
                    self.controller.channelMessages[i][1].append({"sender": self.controller.transportProtocolInUse.username, "text": msgText, "time":msgTime})
                    self.controller.frames["ChattingFrame"].msgListFrame.chatName.configure(text=self.controller.currentChat)
                    showChat(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[i][1])
            else:
                try:                
                    await self.controller.transportProtocolInUse.message_user(self.controller.currentChat, msgText)
                    i = 0
                    while self.controller.userMessages[i][0] != self.controller.currentChat:
                        i+=1
                    self.controller.userMessages[i][1].append({"sender":self.controller.transportProtocolInUse.username, "text": msgText, "time":msgTime})
                    self.controller.frames["ChattingFrame"].msgListFrame.chatName.configure(text=self.controller.currentChat)
                    showChat(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.userMessages[i][1])
                except Exception as e:
                    print("Error:", e)
                    
                    if str(e) != "User not found":
                        return
                    i = 0
                    while self.controller.userMessages[i][0] != self.controller.currentChat:
                        i+=1
                    self.controller.userMessages[i][1].append({"sender":"", "text": "Failed to send Message. User not found", "time":msgTime})
                    self.controller.frames["ChattingFrame"].msgListFrame.chatName.configure(text=self.controller.currentChat)
                    showChat(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.userMessages[i][1])
                    
        else:
            print("Cannot send messages to the server, ignoring button press")
            return
        
class ChattingFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.chatListFrame = Chatting_ChatListFrame(self, controller)
        self.usernameFrame = Chatting_UsernameFrame(self, controller)
        self.signoutFrame = Chatting_SignOutFrame(self, controller)
        self.msgListFrame = Chatting_MessageListFrame(self, controller)

        self.usernameFrame.place(relx=0.15, rely=0.075, relwidth=0.3, relheight=0.15, anchor="center")
        self.chatListFrame.place(relx=0.15, rely=0.525, relwidth=0.3, relheight=0.75, anchor="center")
        self.signoutFrame.place(relx=0.15, rely=0.95, relwidth=0.3, relheight=0.1, anchor="center")
        self.msgListFrame.place(relx=0.65, rely=0.5, relwidth=0.7, relheight=1, anchor="center")

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
        
        self.server_key = base64.b64decode(b'ZixewENi85M3vxEUIu0TC5/nrzuUsHAT4ZTdhc8BC0M=')

    @async_handler
    async def signIn(self):
        #print("Signing in!", self.entryPrivateKey.get())
        private_key = base64.b64decode(bytes(self.entryPrivateKey.get(), 'utf-8'))
        self.entryPrivateKey.delete(0, "end")
        
        if self.ExtendedTransport == False:
            self.controller.transportProtocolInUse = ChatClient(ChatProtocol(EncryptionProtocol(Encryption(private_key, self.server_key))))
        else:
            self.controller.transportProtocolInUse = ChatClient(ChatProtocol(ExtendedEncryptionProtocol(ExtendedEncryption(private_key, self.server_key))))
        
        self.controller.transportProtocolInUse.on_event = self.controller.eventHandler.handleEvent
        message = await self.controller.transportProtocolInUse.connect()
    	
    	#print(message)
    	
        msgTime = datetime.now().strftime("%H:%M:%S")
    	
        self.controller.chatsWithUsers.clear()
        self.controller.chatsWithChannels.clear()
        self.controller.chatsWithChannels.append("Server")
        self.controller.channelMessages.clear()
        self.controller.channelMessages.append(("Server", [{"sender":"Server", "text": message, "time":msgTime}]))
        self.controller.userMessages.clear()
    	
        self.controller.currentChat = "Server"
        self.controller.showChannel = False
    	
        self.controller.frames["ChattingFrame"].chatListFrame.selectChatType("My Chats")
    	
    	#print(self.controller.messages[0])
        self.controller.frames["ChattingFrame"].msgListFrame.chatName.configure(text="Server")
        showChat(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[0][1])
    	#print(self.controller.transportProtocolInUse.username)
    	
        self.controller.updateUsersTask = asyncio.create_task(self.controller.updateUsers())
        self.controller.updateChannelsTask = asyncio.create_task(self.controller.updateChannels())
    	
        self.controller.frames["ChattingFrame"].usernameFrame.lblUsername.configure(text = self.controller.transportProtocolInUse.username)	
        self.controller.changeFrame("ChattingFrame")

class ChangeUsernameFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        #self.vcmd = (self.controller.register(self.validate_and_color), '%P', '%d', '%W')

        self.entryUsername = customtkinter.CTkEntry(master=self, placeholder_text="Enter your new username here.") #, validate="key", validatecommand=self.vcmd)
        self.entryUsername.place(relx=0.5, rely=0.25, relwidth=0.7, relheight=0.25, anchor="center")
        self.entryUsername.bind("<KeyRelease>", self.checkUsername)

        self.userNameToolTip = CTkToolTip(self.entryUsername, message="Username must be unique\nCleartext user's names will auomatically be padded with \'clear-\'\nUsernames cannot contain \':\'\n Usernames are limited to 20 chars total")

        self.btnChangeUsername = customtkinter.CTkButton(self, text="Confirm Name", command=lambda: self.changeUsername())
        self.btnChangeUsername.place(relx=0.25, rely=0.75, relwidth=0.45, relheight=0.3, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("ChattingFrame"))
        self.btnCancel.place(relx=0.75, rely=0.75, relwidth=0.45, relheight=0.3, anchor=customtkinter.CENTER)
        
    def checkUsername(self, event):
        username = self.entryUsername.get()
        valid = True
                
        if len(username) > 20:
            self.entryUsername.delete(0, "end")
            self.entryUsername.insert(0, username[0:20])
        
        if ":" in username:
            valid = False

        if self.controller.isCleartext:
            if not(username.startswith("clear-")):
                self.entryUsername.delete(0, "end")
                self.entryUsername.insert(0, "clear-" + username[5:20])
        
        if len(username) < 7:
            valid = False
        
        if not valid:
            self.entryUsername.configure(text_color="red")
        else:
            self.entryUsername.configure(text_color="white")
        return valid

    @async_handler
    async def changeUsername(self):
        print("Changing username!", self.entryUsername.get())
        username = self.entryUsername.get()
        
        if not self.checkUsername(None):
            print("Failed Validation")
            return
        
        self.entryUsername.delete(0, "end")
        if self.controller.isCleartext:
            if not(username.startswith("clear-")):
                return
        print("new username:", username)
        length = len(username)
        if (length > 20):
            return
        
        oldUsername = self.controller.transportProtocolInUse.username
        response = await self.controller.transportProtocolInUse.set_username(username)
        
        for msg in self.controller.userMessages:
            for text in msg[1]:
                if text["sender"] == oldUsername:
                    text["sender"] = response
        for channelMsgs in self.controller.channelMessages:
            for text in channelMsgs[1]:
                if text["sender"] == oldUsername:
                    text["sender"] = response
        #print(response)
        
        self.controller.frames["ChattingFrame"].usernameFrame.lblUsername.configure(text = self.controller.transportProtocolInUse.username)
        self.controller.changeFrame("ChattingFrame")

class ChannelDetailsFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.channel = None

        self.channelDetails = customtkinter.CTkTextbox(master=self)
        self.channelDetails.insert("0.0", ("channel Details here!!!"))
        self.channelDetails.configure(state="disabled")
        self.channelDetails.place(relx=0.5, rely=0.35, relwidth=0.7, relheight=0.67, anchor="center")

        self.btnJoinOrLeaveChannel = customtkinter.CTkButton(self, text="Join Channel", command=lambda: self.JoinChannel())
        self.btnJoinOrLeaveChannel.place(relx=0.255, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("ChattingFrame"))
        self.btnCancel.place(relx=0.745, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)

    @async_handler
    async def JoinChannel(self):
        print("Joining Channel!!")
        if self.channel:
            response = await self.controller.transportProtocolInUse.join_channel(self.channel)
            self.controller.chatsWithChannels.append(response["channel"])
            self.controller.channelMessages.append((response["channel"], []))
            print("Joined channel: ", response["channel"])
        self.controller.frames["ChattingFrame"].chatListFrame.selectChatType("My Chats")
        self.controller.frames["ChattingFrame"].chatListFrame.openChannel(self.channel)
        self.controller.changeFrame("ChattingFrame")
    
    @async_handler
    async def LeaveChannel(self):
        print("Attrempting to leave channel")
        if self.channel:
            response = await self.controller.transportProtocolInUse.leave_channel(self.channel)
            i = 0
            while self.controller.chatsWithChannels[i] != response["channel"]:
                i += 1
            channel = self.controller.chatsWithChannels.pop(i)
            i = 0
            while self.controller.channelMessages[i][0] != response["channel"]:
                i += 1
            channel = self.controller.channelMessages.pop(i)
            print("Left channel: ", channel)
            self.controller.frames["ChattingFrame"].chatListFrame.selectChatType("My Chats")
            self.controller.frames["ChattingFrame"].chatListFrame.openChannel("Server")
            self.controller.changeFrame("ChattingFrame")

class NewChannelFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.entryChannelName = customtkinter.CTkEntry(master=self, placeholder_text="Enter new channel name here.")
        self.entryChannelName.place(relx=0.5, rely=0.125, relwidth=0.7, relheight=0.2, anchor="center")
        self.entryChannelName.bind("<KeyRelease>", self.checkChannel)

        self.channelNameToolTip = CTkToolTip(self.entryChannelName, message="Channel name can only contain letters, numbers, underscores and dashes and is limited to 20 chars.\nEach user can create atmost 20 channels at a time.\n Any excess will be trimmed.")
        
        self.entryChannelDesc = customtkinter.CTkTextbox(master=self)
        self.entryChannelDesc.insert("0.0", "Enter new channel decription here.")
        self.entryChannelDesc.place(relx=0.5, rely=0.45, relwidth=0.7, relheight=0.4, anchor="center")
        self.entryChannelDesc.bind("<KeyRelease>", self.checkChannelDesc)

        self.channelDescToolTip = CTkToolTip(self.entryChannelDesc, message="Channel description is limited to 100 chars.\n Any excess will be trimmed.")

        self.btnCreateChannel = customtkinter.CTkButton(self, text="Create Channel", command=lambda: self.CreateChannel())
        self.btnCreateChannel.place(relx=0.255, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("ChattingFrame"))
        self.btnCancel.place(relx=0.745, rely=0.84, relwidth=0.47, relheight=0.25, anchor=customtkinter.CENTER)

    def checkChannel(self, event):
        channel = self.entryChannelName.get()
        valid = True
        
        if len(channel) > 20:
            self.entryChannelName.delete(0, "end")
            self.entryChannelName.insert(0, channel[0:20])
        
        if not channel.replace("_", "").replace("-", "").isalnum():
            valid = False

        if len(channel) == 0:
            valid = False
        
        if not valid:
            self.entryChannelName.configure(text_color="red")
        else:
            self.entryChannelName.configure(text_color="white")
        return valid

    def checkChannelDesc(self, event):
        desc = self.entryChannelDesc.get("1.0", "end-1c")
        valid = True
                
        if len(desc) > 100:
            self.entryChannelDesc.delete("1.0", "end-1c")
            self.entryChannelDesc.insert("1.0", channel[0:100])
        
        if not valid:
            self.entryChannelDesc.configure(text_color="red")
        else:
            self.entryChannelDesc.configure(text_color="white")
        return valid

    @async_handler
    async def CreateChannel(self):
        if not self.checkChannel(None):
            return
        
        if not self.checkChannelDesc(None):
            return
        
        name = self.entryChannelName.get()
        self.entryChannelName.delete(0, "end")
        
        desc = self.entryChannelDesc.get("1.0", "end-1c")
        self.entryChannelDesc.delete("1.0", "end")
        
        print("Attempting to create channel")
        
        response = await self.controller.transportProtocolInUse.create_channel(name, desc) 
        
        print("Created Channel")
        
        self.controller.channels.append(response["channel"])
        self.controller.chatsWithChannels.append(response["channel"])
        self.controller.channelMessages.append((response["channel"], []))
        
        self.controller.frames["ChattingFrame"].chatListFrame.selectChatType("My Chats")
        self.controller.frames["ChattingFrame"].chatListFrame.openChannel(name)
        self.controller.changeFrame("ChattingFrame")

class UserDetailsFrame(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.userDetails = customtkinter.CTkTextbox(master=self)
        self.userDetails.insert("0.0", ("user Details here!!!"))
        self.userDetails.configure(state="disabled")
        self.userDetails.place(relx=0.5, rely=0.35, relwidth=0.7, relheight=0.67, anchor="center")

        self.btnMsgUser = customtkinter.CTkButton(self, text="Message User", command=lambda: self.MsgUser())
        self.btnMsgUser.place(relx=0.25, rely=0.85, relwidth=0.45, relheight=0.27, anchor=customtkinter.CENTER)
        
        self.btnCancel = customtkinter.CTkButton(self, text="Cancel", command=lambda: controller.changeFrame("ChattingFrame"))
        self.btnCancel.place(relx=0.75, rely=0.85, relwidth=0.45, relheight=0.27, anchor=customtkinter.CENTER)

    def MsgUser(self):
        print("Start chat with user!!")
        
        if self.transport != "cleartext" and self.controller.isCleartext:
            self.userDetails.configure(state="normal")
            self.userDetails.delete("1.0", "end")
            self.userDetails.insert("0.0", ("Cannot directly message a Wireguard user as a cleartext user"))
            self.userDetails.configure(state="disabled")
        
        if (not(self.username in self.controller.chatsWithUsers)):
            self.controller.chatsWithUsers.append(self.username)
            self.controller.userMessages.append((self.username, []))
        
        self.controller.frames["ChattingFrame"].chatListFrame.selectChatType("My Chats")
        self.controller.frames["ChattingFrame"].chatListFrame.openChat(self.username)
        self.controller.changeFrame("ChattingFrame")

if "__main__" == __name__:
    app = ChatUI()
    app.mainloop()
