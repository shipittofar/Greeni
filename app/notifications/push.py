# app/notifications/push.py
import requests

class PushService:
    def __init__(self, api_key: str, config: dict = None):
        self.api_key = api_key
        self.config = config or {}

    def send_push(self, recipient: str, title: str, body: str, data: dict = None):
        # TODO: وصل کردن به FCM یا OneSignal
        print(f"[Push] Sending to {recipient}: {title} - {body} | {data}")
