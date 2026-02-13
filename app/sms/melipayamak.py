from app.sms.base import BaseSMSService
import requests

class MeliPayamakService(BaseSMSService):
    def send(self, message: str, mobile: str):
        data = {
            "username": self.api_key,
            "password": self.sender,  # فرض مثال
            "to": mobile,
            "text": message
        }
        response = requests.post("https://rest.payamak-panel.com/api/SendSMS", data=data)
        print("meli")
        return response.json()
