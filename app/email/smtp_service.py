# app/email/smtp_service.py
class SMTPEmailService:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.smtp_server = host  # نگه داشتن نام داخلی smtp_server برای سازگاری
        self.port = port
        self.username = username
        self.password = password

    def send(self, to: str, subject: str, body: str):
        # ارسال ایمیل واقعی یا چاپ لاگ برای تست
        print(f"Sending email to {to} with subject {subject}")
