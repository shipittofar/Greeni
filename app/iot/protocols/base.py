from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel


class ProtocolConfig(BaseModel):
    """پیکربندی عمومی پروتکل"""
    sampling_interval: int = 1000  # میلی‌ثانیه
    timeout: int = 5000  # میلی‌ثانیه
    retry_count: int = 3
    
    class Config:
        extra = "allow"  # اجازه فیلدهای اضافی بر اساس پروتکل


class ProtocolResponse(BaseModel):
    """پاسخ استاندارد پروتکل"""
    success: bool
    value: Optional[Any] = None
    unit: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[float] = None


class BaseProtocol(ABC):
    """کلاس پایه برای تمام پروتکل‌ها"""
    
    PROTOCOL_NAME = "base"
    
    def __init__(self, pin_mapping: Dict[str, int], config: Dict[str, Any]):
        """
        Args:
            pin_mapping: نقشه‌برداری پین‌ها (مثلاً {"data": 17, "clock": 27})
            config: پیکربندی پروتکل (sampling_interval، timeout، etc)
        """
        self.pin_mapping = pin_mapping or {}
        self.config = ProtocolConfig(**config) if config else ProtocolConfig()
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> ProtocolResponse:
        """اولین راه‌اندازی پروتکل و اتصال"""
        pass
    
    @abstractmethod
    def read_value(self, attribute_name: str) -> ProtocolResponse:
        """خواندن مقدار از سنسور"""
        pass
    
    @abstractmethod
    def write_value(self, attribute_name: str, value: Any) -> ProtocolResponse:
        """نوشتن مقدار به سنسور"""
        pass
    
    @abstractmethod
    def disconnect(self) -> ProtocolResponse:
        """قطع اتصال"""
        pass
    
    def validate_pin_mapping(self, required_pins: List[str]) -> bool:
        """بررسی اینکه تمام پین‌های لازم موجود هستند"""
        return all(pin in self.pin_mapping for pin in required_pins)
    
    @staticmethod
    def get_protocol_schema() -> Dict[str, Any]:
        """سکیمای کانفیگ پروتکل"""
        return {
            "type": "object",
            "properties": {
                "sampling_interval": {"type": "integer", "default": 1000},
                "timeout": {"type": "integer", "default": 5000},
                "retry_count": {"type": "integer", "default": 3},
            }
        }