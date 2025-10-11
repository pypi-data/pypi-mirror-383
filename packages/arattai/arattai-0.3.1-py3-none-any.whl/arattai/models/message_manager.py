import time
from .chats import Chat
import mimetypes


class MessageSender:
    def __init__(self,session):
        self.session = session
        self.m_send_url = "https://web.arattai.in/sendofficechatmessage.do"
        self.f_send_url = "https://files.arattai.in/webupload"
        
    def send_message(self,message,chat_id=None,dname=None,chat:Chat=None):
        if(chat_id == None and chat == None):
            print("Please pass either chat_id or Chat object")
            return False
        if(chat):
            chat_id = chat.get_chat_id()
            dname = chat.owner.get_dname()
        data = {
            "chid":chat_id,
            "msg":message,
            "msgid":int(time.time()*1000),
            "dname":dname,
            "unfurl":"true"
        }
        self.session.post(self.m_send_url,data=data)
    def send_file(self,file_path,caption="",chat_id=None,dname=None,chat:Chat=None):
        if(chat_id == None and chat == None):
            print("Please pass either chat_id or Chat object")
            return False
        
        if(chat):
            chat_id = chat.get_chat_id()
            dname = chat.owner.get_dname()
        timestamp = int(time.time()*1000)
        mime_type, encoding = mimetypes.guess_type(file_path)
        headers = {
            "x-cliq-content-type":mime_type,
            "x-cliq-comment":caption,
            "upload-id":chat_id+"_"+str(timestamp),
            "x-cliq-msgid":str(timestamp),
            "file-name":"Please fill it asap",
            "Content-type":mime_type,
            "x-service":"arattai",
            "x-cliq-sid":"a",
            "x-client-time-utc":str(timestamp),
            "x-cliq-id":chat_id
        }
        with open(file_path,"rb") as f:
            file = f.read()
        self.session.post(self.f_send_url,data=file,headers=headers)
        
            