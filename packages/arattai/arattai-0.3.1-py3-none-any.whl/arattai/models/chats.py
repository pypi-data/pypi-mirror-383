import json
import traceback

class Message:
    def __init__(self,msguid,msg):
        self.msguid = msguid
        self.msg = msg

        
class Participant:
    def __init__(self,dname,zuid):
        self.dname = dname
        self.zuid = zuid
    
        
    def get_dname(self):
        return self.dname
    
    def get_zuid(self):
        return self.zuid

        
class Chat:
    def __init__(self,chat_id,title,owner,participants:list[Participant],message:list[Message],lastmsguid):
        self.chat_id = chat_id
        self.title=title
        self.owner = owner
        self.participants = participants
        self.message = message
        self.lastmsguid = lastmsguid
        
    def __repr__(self):
        pr = {
            "chat_id":self.chat_id,
            "title":self.title,
            "self.lastmsguid":self.lastmsguid
        }
        return json.dumps(pr,indent=2)
    
    def get_chat_id(self):
        return self.chat_id
    
    def get_title(self):
        return self.title
    
    def get_owner(self):
        return self.owner
    
    def get_participants(self):
        return self.participants
    
    def get_message(self):
        return self.message
    
    def get_lastmsguid(self):
        return self.lastmsguid
        
    def add_message(self,message:list[Message]):
        self.message.append(message)
    
    def get_message(self,limit:int=10):
        return self.message[-limit] if limit else self.message
        
        
class ChatManager:
    def __init__(self,chat_data):
        self.chats = {}
        self.chat_data = chat_data
        
        
    def get_chats(self):
        return self.chats
        
    def parse_chat_data(self):
        try:
            for data in self.chat_data["data"]["chats"]:
                all_participants = []

                if("recipants" in data):
                    recipants = json.loads(data['recipants'])
                    for participant in recipants:
                        zuid = participant["zuid"]
                        dname = participant["dname"]
                        all_participants.append(Participant(zuid,dname))

                if("lastmsginfo" in data and data['lastmsginfo'] != ""):
                    lastmsginfo = json.loads(data['lastmsginfo'])
                    lastmsguid = lastmsginfo["msguid"]
                    msg = Message(lastmsginfo["msg"],lastmsginfo["msguid"])
                else:
                    lastmsguid = None
                    msg = None
                owner = Participant(data["owner"]["name"],data["owner"]["id"])
                title = data["title"]
                chat_id = data["chatid"]
                self.chats.update({chat_id:Chat(chat_id,title,owner,all_participants,msg,lastmsguid)})
            return self.chats
        except Exception as e:
            traceback.print_exc()
        
                    
                    
                
            