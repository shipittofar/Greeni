from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_lib

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    unique_code = Column(String, unique=True, nullable=False)
    ip_address = Column(String, nullable=True)
    mac_address = Column(String, nullable=True)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    lat = Column(String, nullable=True)
    lon = Column(String, nullable=True)
    time_zone = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    category = Column(String, nullable=True)
    product_id = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    local_key = Column(String, nullable=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid_lib.uuid4())
    is_pending = Column(Boolean, default=True)
    is_system_registered = Column(Boolean, default=False)
    is_multimedia = Column(Boolean, default=False, nullable=True)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sensors = relationship("Sensor", back_populates="device")
    data_points = relationship("DeviceData", back_populates="device", cascade="all, delete-orphan")
    cameras = relationship("Camera", back_populates="device", cascade="all, delete-orphan")
    
    def to_dict(self, include_relations=False):
        """
        تبدیل Device model به dictionary
        
        Args:
            include_relations (bool): آیا relationships رو شامل کنیم؟
        
        Returns:
            dict: Device data به شکل dictionary
        """
        data = {
            "id": self.id,
            "name": self.name,
            "unique_code": self.unique_code,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "description": self.description,
            "location": self.location,
            "lat": self.lat,
            "lon": self.lon,
            "time_zone": self.time_zone,
            "icon": self.icon,
            "category": self.category,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "local_key": self.local_key,
            "uuid": str(self.uuid) if self.uuid else None,
            "is_pending": self.is_pending,
            "is_system_registered": self.is_system_registered,
            "is_multimedia": self.is_multimedia,
            "is_active": self.is_active,
            "is_online": self.is_online,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # اگر relationships رو شامل کنیم (احتیاط از circular reference!)
        if include_relations:
            # sensors رو شامل کن (اگر exists method دارند)
            if self.sensors and hasattr(self.sensors[0], 'to_dict'):
                data["sensors"] = [sensor.to_dict() for sensor in self.sensors]
            else:
                data["sensors"] = []
            
            # data_points رو شامل کن
            if self.data_points and hasattr(self.data_points[0], 'to_dict'):
                data["data_points"] = [dp.to_dict() for dp in self.data_points]
            else:
                data["data_points"] = []
        
        return data
    
    def to_dict_simple(self):
        """
        تبدیل سریع Device به dictionary بدون relationships
        برای بهتر شدن performance
        """
        return {
            "id": self.id,
            "name": self.name,
            "unique_code": self.unique_code,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "category": self.category,
            "product_name": self.product_name,
            "uuid": str(self.uuid) if self.uuid else None,
            "is_active": self.is_active,
            "is_online": self.is_online,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
        }
    
    def __repr__(self):
        return f"<Device(id={self.id}, name={self.name}, unique_code={self.unique_code})>"