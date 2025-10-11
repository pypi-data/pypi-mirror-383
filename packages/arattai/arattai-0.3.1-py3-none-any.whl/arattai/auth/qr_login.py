import time
import qrcode

class QRLogin:
    def __init__(self, session):
        self.qr_generate_url = "https://accounts.arattai.in/signin/v2/qrcode"
        self.base_url = "https://web.arattai.in"
        self.session = session
        self.stop_flag = False
        self.qr_resp = None
        self.cli_time = int(time.time()*1000)
        proxies = {"http": "http://127.0.0.1:8888","https": "http://127.0.0.1:8888"}
        session.proxies.update(proxies)
        session.verify = False
        
        
    def prepare_qr(self):
        self.session.get("https://accounts.arattai.in", allow_redirects=True)
        params = {
            "QRLogin": True,
            "servicename": "Arattai",
            "serviceurl": self.base_url
        }
        resp = self.session.get(self.qr_generate_url.replace("/v2/qrcode",""), params=params)

        
        
    def request_qr_data(self):
        self.prepare_qr()
        self.cli_time = int(time.time()*1000)
        params = {
            "cli_time": self.cli_time,
            "servicename": "Arattai",
            "serviceurl": self.base_url
        }
        csrf_token = self.session.cookies.get("iamcsr")
        self.session.headers.update({
            "X-ZCSRF-TOKEN": "iamcsrcoo="+csrf_token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        })

        
        print("Cookies after prepare_qr:", self.session.cookies.get_dict())

        resp = self.session.post(
            self.qr_generate_url,
            params=params,
            data='{"qrcodeauth":{"remember":true}}'
        )
        self.qr_resp = resp.json()
        return resp.json()
    
    
    def show_qr(self):
        if(self.qr_resp["qrcodeauth"]["token"]):
            qr_data = self.qr_resp["qrcodeauth"]["oneauth_url"]
            qr_img = qrcode.QRCode(box_size=1,version=None,border=1)
            qr_img.add_data(qr_data)
            qr_img.make(fit=True)
            qr_img.print_ascii(invert=True)
            return True
        else:
            return False
    
    def validate_qr(self):
        while(not self.stop_flag):
            if(not self.qr_resp or not self.qr_resp["qrcodeauth"]["token"]):
                self.request_qr_data()
                self.show_qr()
            else:
                params = {
                    "cli_time": self.cli_time,
                    "servicename": "AaaServer",
                    "serviceurl": self.base_url
                }
                body = '{"qrcodeauth":{"remember":true}}'
                token = self.qr_resp["qrcodeauth"]["token"]
                self.session.headers.update({
                    "Z-Authorization":"Zoho-ticket "+token
                })

                resp = self.session.put(
                    self.qr_generate_url,
                    params=params,
                    data='{"qrcodeauth":{"remember":true}}'
                )
                status_code = resp.json()["status_code"]
                if(status_code == 401):
                    self.request_qr_data()
                    self.show_qr()
                    pass
                elif(status_code == 200):
                    print("Authentication Successful")
                    self.stop_flag = True
                    return True
                
                time.sleep(5)

    
    def initiate_login(self):
        return self.validate_qr()
    
        