from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt, ExpiredSignatureError
from typing import Optional, Union
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    هش کردن پسورد برای ذخیره در دیتابیس
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    تایید تطابق پسورد ورودی با هش شده
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[Union[timedelta, None]] = None) -> str:
    """
    ساخت توکن دسترسی (Access Token) با زمان انقضا دلخواه یا پیش‌فرض
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "scope": "access_token"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[Union[timedelta, None]] = None) -> str:
    """
    ساخت توکن تازه‌سازی (Refresh Token) با زمان انقضا دلخواه یا پیش‌فرض
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "scope": "refresh_token"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """
    رمزگشایی توکن و بازگرداندن payload در صورت معتبر بودن، در غیر این صورت None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except ExpiredSignatureError:
        # توکن منقضی شده
        return None
    except JWTError:
        # توکن نامعتبر یا خراب
        return None
