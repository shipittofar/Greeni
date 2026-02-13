from app.sms.base import BaseSMSService
import requests

class SMSIRService(BaseSMSService):
    def __init__(self, api_key: str, sender: str):
        self.api_key = api_key
        self.sender = sender

    def send(self, to: str, message: str):
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        data = {
            "mobile": to,
            "templateId": 793797,
            "parameters": [{"name": "Code", "value": message}]
        }

        response = requests.post("https://api.sms.ir/v1/send/verify", json=data, headers=headers)
        if response.status_code != 200 or response.json().get("status") != 1:
            raise Exception(f"خطا در ارسال پیامک: {response.text}")

        print("smsir")
        return response.json()
