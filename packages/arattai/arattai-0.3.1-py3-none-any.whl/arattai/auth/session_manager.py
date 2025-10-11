import pickle
class SessionManager:
    def __init__(self,session):
        self.session = session
        
    def save_cookies(self,filename:str="cookies.pkl"):
        with open(filename,"wb") as f:
            pickle.dump(self.session.cookies.get_dict(),f)
    
    def save_headers(self,filename:str="headers.pkl"):
        with open(filename,"wb") as f:
            pickle.dump(dict(self.session.headers),f)
    
    def load_cookies(self,filename:str="cookies.pkl"):
        with open(filename,"rb") as f:
            cookies = pickle.load(f)
        for k,v in cookies.items():
            self.session.cookies.set(k,v)
            
    def load_headers(self,filename:str="headers.pkl"):
        with open(filename,"rb") as f:
            headers = pickle.load(f)
        self.session.headers.update(headers)
    
    def save_session(self):
        self.save_cookies()
        self.save_headers()
    
    def load_session(self):
        self.load_headers()
        self.load_cookies()
    
    def testCookies(self):
        try:
            self.load_session()
            self.load_cookies()
        except Exception as e:
            return False
        url = "https://web.arattai.in/"
        resp = self.session.get(url,timeout=10)
        if(resp.url != url):
            return False
        else:
            return True
        