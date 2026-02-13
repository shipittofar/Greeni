from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.user import User
from app.dependencies.auth import get_db, get_current_user
from app.core.security import create_access_token, create_refresh_token, verify_password, decode_token
from datetime import timedelta
from app.core.config import settings
from app.schemas.user import UserPublic as UserSchema  # یا UserOut
from app.crud import user as user_crud
router = APIRouter()

@router.post("/token", summary="Login To Get Token", tags=["Authentication"])
# def login(form_data: OAuth2PasswordRequestForm = Depends(), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == form_data.username).first()
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="شماره تلفن یا رمز عبور اشتباه است"
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری مسدود است"
        )
        
    user_crud.add_login_timestamp(db, user)


    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "phone_number": user.phone_number},
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", summary="Refresh Access Token", tags=["Authentication"])
def refresh_token(current_user: User = Depends(get_current_user), refresh_token: str = Body(..., embed=True)):
    payload = decode_token(refresh_token)
    if payload is None or payload.get("scope") != "refresh_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن رفرش نامعتبر است"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن رفرش نامعتبر است"
        )

    new_access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserSchema, summary="Get Current User", tags=["Authentication"])
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", summary="Logout User", tags=["Authentication"])
def logout(current_user: User = Depends(get_current_user)):
    # چون JWT استیتلس است، logout در سمت کلاینت انجام می‌شود (پاک کردن توکن)
    # اگر بخواهید blacklist پیاده کنید، باید اینجا ذخیره کنید.
    return {"msg": "خروج با موفقیت انجام شد. لطفا توکن‌ها را در کلاینت پاک کنید."}
