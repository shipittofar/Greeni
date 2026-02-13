# app/schemas/push_provider.py
from pydantic import BaseModel
from typing import Optional, Dict

class PushProviderBase(BaseModel):
    name: str
    api_key: str
    config: Optional[Dict] = None
    is_active: Optional[bool] = True

class PushProviderCreate(PushProviderBase):
    pass

class PushProviderUpdate(BaseModel):
    api_key: Optional[str]
    config: Optional[Dict]
    is_active: Optional[bool]

class PushProviderOut(PushProviderBase):
    id: int

    class Config:
        from_attributes = True

