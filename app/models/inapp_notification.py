# app/models/inapp_notification.py
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.base_class import Base

class InAppNotification(Base):
    __tablename__ = "inapp_notifications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info", nullable=False)  # info, warning, error, success
    action_url = Column(String, nullable=True)  # URL for notification action
    action_label = Column(String(255), nullable=True)  # Label for action button
    data = Column(JSON, nullable=True)  # Additional JSON data
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert SQLAlchemy model instance to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'action_url': self.action_url,
            'action_label': self.action_label,
            'data': self.data,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<InAppNotification(id={self.id}, user_id={self.user_id}, title='{self.title}')>"