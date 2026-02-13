from typing import Dict, Any, Optional, Type
from .base import BaseProtocol, ProtocolResponse
from .gpio import GPIOProtocol
from .i2c import I2CProtocol
from .spi import SPIProtocol
from .uart import UARTProtocol
from .pwm import PWMProtocol
from .modbus import ModbusProtocol
from .lora import LoRaProtocol
from .zigbee import ZigbeeProtocol


class ProtocolFactory:
    """Factory برای ایجاد instance‌های پروتکل"""
    
    _protocols: Dict[str, Type[BaseProtocol]] = {
        "GPIO": GPIOProtocol,
        "I2C": I2CProtocol,
        "SPI": SPIProtocol,
        "UART": UARTProtocol,
        "PWM": PWMProtocol,
        "MODBUS": ModbusProtocol,
        "LORA": LoRaProtocol,
        "ZIGBEE": ZigbeeProtocol,
    }
    
    @classmethod
    def register_protocol(cls, name: str, protocol_class: Type[BaseProtocol]):
        """ثبت پروتکل جدید"""
        cls._protocols[name.upper()] = protocol_class
    
    @classmethod
    def create_protocol(
        cls,
        protocol_name: str,
        pin_mapping: Dict[str, int],
        config: Dict[str, Any]
    ) -> Optional[BaseProtocol]:
        """ایجاد instance از پروتکل"""
        protocol_class = cls._protocols.get(protocol_name.upper())
        
        if not protocol_class:
            raise ValueError(
                f"پروتکل '{protocol_name}' پشتیبانی نمی‌شود. "
                f"پروتکل‌های موجود: {list(cls._protocols.keys())}"
            )
        
        return protocol_class(pin_mapping, config)
    
    @classmethod
    def get_available_protocols(cls) -> Dict[str, Type[BaseProtocol]]:
        """دریافت تمام پروتکل‌های ثبت‌شده"""
        return cls._protocols.copy()
    
    @classmethod
    def get_protocol_schema(cls, protocol_name: str) -> Dict[str, Any]:
        """دریافت سکیمای پروتکل"""
        protocol_class = cls._protocols.get(protocol_name.upper())
        
        if not protocol_class:
            raise ValueError(f"پروتکل '{protocol_name}' پیدا نشد")
        
        return protocol_class.get_protocol_schema()


class ProtocolManager:
    """مدیر پروتکل‌ها - نقطه دسترسی اصلی"""
    
    def __init__(self):
        self._active_protocols: Dict[int, BaseProtocol] = {}  # sensor_id -> protocol
    
    def initialize_sensor_protocol(
        self,
        sensor_id: int,
        protocol_name: str,
        pin_mapping: Dict[str, int],
        config: Dict[str, Any]
    ) -> ProtocolResponse:
        """راه‌اندازی پروتکل برای سنسور"""
        try:
            protocol = ProtocolFactory.create_protocol(
                protocol_name,
                pin_mapping,
                config
            )
            
            if not protocol:
                return ProtocolResponse(
                    success=False,
                    error=f"نتوانست پروتکل '{protocol_name}' ایجاد کند"
                )
            
            # راه‌اندازی پروتکل
            response = protocol.initialize()
            
            if response.success:
                self._active_protocols[sensor_id] = protocol
            
            return response
        except Exception as e:
            return ProtocolResponse(
                success=False,
                error=f"خطا در راه‌اندازی پروتکل: {str(e)}"
            )
    
    def read_sensor_value(
        self,
        sensor_id: int,
        attribute_name: str
    ) -> ProtocolResponse:
        """خواندن مقدار سنسور"""
        protocol = self._active_protocols.get(sensor_id)
        
        if not protocol:
            return ProtocolResponse(
                success=False,
                error=f"پروتکل برای سنسور {sensor_id} فعال نیست"
            )
        
        return protocol.read_value(attribute_name)
    
    def write_sensor_value(
        self,
        sensor_id: int,
        attribute_name: str,
        value: Any
    ) -> ProtocolResponse:
        """نوشتن مقدار سنسور"""
        protocol = self._active_protocols.get(sensor_id)
        
        if not protocol:
            return ProtocolResponse(
                success=False,
                error=f"پروتکل برای سنسور {sensor_id} فعال نیست"
            )
        
        return protocol.write_value(attribute_name, value)
    
    def disconnect_sensor(self, sensor_id: int) -> ProtocolResponse:
        """قطع اتصال سنسور"""
        protocol = self._active_protocols.get(sensor_id)
        
        if not protocol:
            return ProtocolResponse(
                success=False,
                error=f"پروتکل برای سنسور {sensor_id} یافت نشد"
            )
        
        response = protocol.disconnect()
        
        if response.success:
            del self._active_protocols[sensor_id]
        
        return response
    
    def get_active_protocols(self) -> Dict[int, str]:
        """دریافت لیست پروتکل‌های فعال"""
        return {
            sensor_id: protocol.PROTOCOL_NAME
            for sensor_id, protocol in self._active_protocols.items()
        }
    
    def get_protocol_instance(self, sensor_id: int) -> Optional[BaseProtocol]:
        """دریافت instance‌ پروتکل برای سنسور"""
        return self._active_protocols.get(sensor_id)


# Global instance
protocol_manager = ProtocolManager()