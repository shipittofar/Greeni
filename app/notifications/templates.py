# app/notifications/templates.py
TEMPLATES = {
    "welcome_email": {
        "subject": "Welcome to Greeni!",
        "body": "Hello, welcome! Your access to this service is our plesure."
    },
    "device_pending": {
        "subject": "Device {DEVICE} Knocking!",
        "body": "You have new device! {DEVICE} knocking!"
    },
    "device_registered": {
        "subject": "Device Registered!",
        "body": "Contrats! Your new device {DEVICE} is now registered."
    },
    "otp_sms": {
        # "body": "Your OTP code is {code}"
        "body": "Your OTP code is "
    },
    "device_alert": {
        "subject": "Device Alert: {DEVICE}",
        "body": "Warning! Device {DEVICE} has triggered an alert."
    },
    "device_alert_push": {
        "title": "Device Alert",
        "body": "Device {DEVICE} triggered an alert!"
    },
    "device_status_change": {
        "title": "Device Status Changed",
        "body": "Device {ID} {DEVICE} is now {STATUS}."
    }
    
}

def render_template(template: str, data: dict):
    tpl = TEMPLATES.get(template)
    if not tpl:
        raise ValueError(f"Template '{template}' not found")
    return {k: v.format(**data) for k, v in tpl.items()}
