from .auth.qr_login import QRLogin
from .auth.session_manager import SessionManager
from .models.bot import Bot
import requests
#from auth.token_login import TokenLogin

class ArattaiBot:
    def __init__(self,isShowQr:bool = True):
        self.isShowQr = isShowQr
        self.token = None
        self.session = requests.Session()
        
        
    def login_with_qr(self):
        session_manager = SessionManager(self.session)
        if(session_manager.testCookies()):
            return Bot(self.session)
        else:
            qr = QRLogin(self.session)
            qr_resp = qr.initiate_login()
            session_manager.save_session()
            if(qr_resp):
                return Bot(self.session)
        
    