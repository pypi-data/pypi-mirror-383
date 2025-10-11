from .chats import Message,Participant,Chat,ChatManager
from .message_manager import MessageSender
import time
class Bot:
    def __init__(self,session):
        self.session = session
        self.chats = []
        self.chat_api = "https://web.arattai.in/v1/chats"
    
    
    def fetch_chats(self,pinned:bool=False,limit:int=20):
        self.session.get("https://web.arattai.in/")
        self.session.headers.update({
            "X-ZCSRF-TOKEN":"zchat_csrparam="+self.session.cookies.get("CT_CSRF_TOKEN"),
        })
        if "Z-Authorization" in self.session.headers:
            del self.session.headers["Z-Authorization"]
        params = {
            #pinned=false&limit=20&fromtime=-1&nocache=1759983948013
            "pinned":str(pinned).lower(),
            "limit":limit,
            "fromtime":"-1",
            "nocache":int(time.time()*1000)
        }
        resp = self.session.get(self.chat_api,params=params).json()
        chat_manager = ChatManager(resp)
        return chat_manager.parse_chat_data()
    
    @property
    def sender(self):
        return MessageSender(self.session)
    
    
    
    