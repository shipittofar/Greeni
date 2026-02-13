from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr
    role_id: Optional[int] = Field(None, gt=0, description="Role ID must be greater than 0 if provided")
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class UserBasicUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = Field(None, gt=0)
    phone_number: Optional[str] = None
    
    
class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_logins: List[datetime] = []
    is_superuser: bool

    model_config = {
        "from_attributes": True
    }


class UserPublic(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr
    is_active: bool
    role_id: Optional[int] = Field(None, gt=0)
    created_at: datetime
    updated_at: Optional[datetime]
    last_logins: List[datetime] = []
    is_superuser: bool

    model_config = {
        "from_attributes": True
    }
