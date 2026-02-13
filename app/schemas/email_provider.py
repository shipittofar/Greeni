# app/schemas/email_provider.py
from pydantic import BaseModel
from typing import Optional

class EmailProviderBase(BaseModel):
    name: str
    host: str
    port: int
    username: str
    password: str
    is_active: bool = False

class EmailProviderCreate(EmailProviderBase):
    pass

class EmailProviderOut(EmailProviderBase):
    id: int

    class Config:
        from_attributes = True

