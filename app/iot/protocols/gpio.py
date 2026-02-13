from typing import Any, Dict
from datetime import datetime
from .base import BaseProtocol, ProtocolResponse

# در production، اینجا import میشود: import RPi.GPIO as GPIO
# برای develop/test: mock یا simulator استفاده کنید


class GPIOProtocol(BaseProtocol):
    """GPIO پروتکل برای خواندن/نوشتن مقادیر دیجیتال"""
    
    PROTOCOL_NAME = "GPIO"
    REQUIRED_PINS = ["pin"]  # حداقل یک پین مورد نیاز است
    
    def __init__(self, pin_mapping: Dict[str, int], config: Dict[str, Any]):
        super().__init__(pin_mapping, config)
        self.gpio_module = None
        self.pin_states = {}
    
    def initialize(self) -> ProtocolResponse:
        """راه‌اندازی GPIO و تنظیم پین‌ها"""
        try:
            if not self.validate_pin_mapping(self.REQUIRED_PINS):
                return ProtocolResponse(
                    success=False,
                    error=f"نقشه‌برداری پین نامعتبر است. پین‌های لازم: {self.REQUIRED_PINS}"
                )
            
            # اینجا قابل شبیه‌سازی است برای تست
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            
            pin = self.pin_mapping.get("pin")
            # GPIO.setup(pin, GPIO.IN)  # یا GPIO.OUT
            
            self.is_initialized = True
            self.pin_states[pin] = None
            
            return ProtocolResponse(
                success=True,
                value="GPIO initialized successfully",
                timestamp=datetime.now().timestamp()
            )
        except Exception as e:
            return ProtocolResponse(
                success=False,
                error=f"خطا در راه‌اندازی GPIO: {str(e)}"
            )
    
    def read_value(self, attribute_name: str) -> ProtocolResponse:
        """خواندن سطح دیجیتال پین"""
        if not self.is_initialized:
            return ProtocolResponse(success=False, error="GPIO initialized نشده است")
        
        try:
            pin = self.pin_mapping.get("pin")
            # value = GPIO.input(pin)
            
            # شبیه‌سازی برای تست:
            value = self.pin_states.get(pin, 0)
            
            return ProtocolResponse(
                success=True,
                value=value,
                unit="Digital (0/1)",
                timestamp=datetime.now().timestamp()
            )
        except Exception as e:
            return ProtocolResponse(success=False, error=str(e))
    
    def write_value(self, attribute_name: str, value: Any) -> ProtocolResponse:
        """نوشتن سطح دیجیتال پین"""
        if not self.is_initialized:
            return ProtocolResponse(success=False, error="GPIO initialized نشده است")
        
        try:
            pin = self.pin_mapping.get("pin")
            digital_value = int(value)
            
            if digital_value not in [0, 1]:
                return ProtocolResponse(
                    success=False,
                    error="مقدار باید 0 یا 1 باشد"
                )
            
            # GPIO.output(pin, digital_value)
            self.pin_states[pin] = digital_value
            
            return ProtocolResponse(
                success=True,
                value=digital_value,
                timestamp=datetime.now().timestamp()
            )
        except Exception as e:
            return ProtocolResponse(success=False, error=str(e))
    
    def disconnect(self) -> ProtocolResponse:
        """تمیز کردن GPIO"""
        try:
            # GPIO.cleanup()
            self.is_initialized = False
            return ProtocolResponse(
                success=True,
                value="GPIO cleaned up successfully"
            )
        except Exception as e:
            return ProtocolResponse(success=False, error=str(e))
    
    @staticmethod
    def get_protocol_schema() -> Dict[str, Any]:
        """سکیمای مخصوص GPIO"""
        base_schema = BaseProtocol.get_protocol_schema()
        base_schema["properties"].update({
            "pin_mode": {
                "type": "string",
                "enum": ["INPUT", "OUTPUT"],
                "default": "INPUT"
            },
            "pull_up": {
                "type": "boolean",
                "default": False
            }
        })
        return base_schema