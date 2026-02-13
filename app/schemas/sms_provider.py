from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SMSProviderBase(BaseModel):
    name: str = Field(..., description="Unique provider name")
    api_key: Optional[str] = Field(None, description="API key for the SMS provider")
    sender: Optional[str] = Field(None, description="Sender ID or number")
    is_active: Optional[bool] = Field(True, description="Is this provider active?")

class SMSProviderCreate(SMSProviderBase):
    pass

class SMSProviderUpdate(BaseModel):
    api_key: Optional[str]
    sender: Optional[str]
    is_active: Optional[bool]

class SMSProviderIsActiveUpdate(BaseModel):
    is_active: Optional[bool]

class SMSProviderInDB(SMSProviderBase):
    id: str
    registered_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

