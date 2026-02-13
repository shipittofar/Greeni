# # app/api/v1/media.py

# import os
# import shutil
# import uuid
# import hashlib
# from datetime import datetime
# from typing import List
# from app.dependencies.db import get_db
# from sqlalchemy.orm import Session


# from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# from fastapi.responses import JSONResponse

# from app.models.user import User
# from app.dependencies.auth import get_current_user

# from app.iot.mqtt.client import mqtt_publish
# from app.core.config import settings
# from app.crud.device import get_all_active_multimedia_device_codes

# from urllib.parse import quote


# router = APIRouter()
# MEDIA_DIR = "media"


# def calculate_file_hash(file) -> str:
#     """Calculate SHA256 hash of uploaded file"""
#     hasher = hashlib.sha256()
#     file.file.seek(0)
#     while chunk := file.file.read(8192):
#         hasher.update(chunk)
#     file.file.seek(0)
#     return hasher.hexdigest()

# def notify_device_download(device_code: str, filename: str):
#     encoded_filename = quote(filename)  # 🔹 encode special chars
#     url = f"{settings.SERVER_HOST}/media/{encoded_filename}"
#     payload = {
#         "type": "MEDIA",
#         "action": "download",
#         "url": url,
#         "file": filename  # نام فایل اصلی رو به دستگاه بده
#     }
#     topic = f"greeni/device/{device_code}/command"
#     mqtt_publish(topic, payload)
#     print(f"[MQTT] Sent download command to {device_code}: {payload}")


# @router.post("/upload")
# async def upload_files(
#     files: List[UploadFile] = File(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     # is_dev
#     # os.makedirs(MEDIA_DIR, exist_ok=True)
#     os.makedirs(MEDIA_DIR, exist_ok=True, mode=0o777)
#     results = []

#     for file in files:
#         file_hash = calculate_file_hash(file)

#         # چک کن فایل مشابه قبلاً وجود داره یا نه
#         for existing in os.listdir(MEDIA_DIR):
#             if existing.endswith(".hash"):
#                 with open(os.path.join(MEDIA_DIR, existing), "r") as f:
#                     if f.read().strip() == file_hash:
#                         # همون فایل پیدا شد
#                         stored_filename = existing.replace(".hash", "")
#                         results.append({
#                             "original_filename": file.filename,
#                             "stored_filename": stored_filename,
#                             "url": f"/media/{stored_filename}",
#                             "duplicate": True,
#                         })
#                         break
#         else:
#             # فایل جدید رو ذخیره کن
#             unique_id = str(uuid.uuid4())
#             date_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
#             safe_name = file.filename.replace(" ", "_")
#             stored_filename = f"{date_str}_{unique_id}_{safe_name}"
#             file_path = os.path.join(MEDIA_DIR, stored_filename)

#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)

#             # هش رو ذخیره کن
#             with open(file_path + ".hash", "w") as f:
#                 f.write(file_hash)

#             # is_dev
#             os.chmod(file_path, 0o666)

#             results.append({
#                 "original_filename": file.filename,
#                 "stored_filename": stored_filename,
#                 "url": f"/media/{stored_filename}",
#                 "duplicate": False,
#             })

#         if not any(r["stored_filename"] == stored_filename and r["duplicate"] for r in results):
#             # برای همه دستگاه‌ها دستور دانلود بفرست
#             for device_code in get_all_active_multimedia_device_codes(db):
#                 notify_device_download(device_code, stored_filename)

#     return {"uploaded": results}


# @router.delete("/delete/{filename}")
# async def delete_file(
#     filename: str,
#     current_user: User = Depends(get_current_user),
# ):
#     file_path = os.path.join(MEDIA_DIR, filename)
#     hash_path = file_path + ".hash"

#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")

#     try:
#         os.remove(file_path)
#         # if os.path.exists(hash_path):
#         #     os.remove(hash_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

#     return JSONResponse(content={"deleted": filename, "status": "success"})

# @router.delete("/delete-all")
# async def delete_all_files(
#     current_user: User = Depends(get_current_user),
# ):
#     if not os.path.exists(MEDIA_DIR):
#         raise HTTPException(status_code=404, detail="Media directory not found")

#     deleted_files = []
#     errors = []

#     try:
#         for filename in os.listdir(MEDIA_DIR):
#             file_path = os.path.join(MEDIA_DIR, filename)

#             # فقط فایل‌های اصلی رو پاک کن (hash حذف نشه)
#             if os.path.isfile(file_path) and not filename.endswith(".hash"):
#                 try:
#                     os.remove(file_path)
#                     deleted_files.append(filename)
#                 except Exception as e:
#                     errors.append({filename: str(e)})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error while scanning directory: {e}")

#     return JSONResponse(
#         content={
#             "status": "success",
#             "deleted_files": deleted_files,
#             "errors": errors,
#             "total_deleted": len(deleted_files),
#         }
#     )


# #delete all with hash's

# @router.delete("/delete-all-hash")
# async def delete_all_files_with_hash(
#     current_user: User = Depends(get_current_user),
# ):
#     if not os.path.exists(MEDIA_DIR):
#         raise HTTPException(status_code=404, detail="Media directory not found")

#     deleted_files = []
#     errors = []

#     try:
#         for filename in os.listdir(MEDIA_DIR):
#             file_path = os.path.join(MEDIA_DIR, filename)

#             # فقط فایل‌های اصلی (نه .hash)
#             if os.path.isfile(file_path):
#                 try:
#                     os.remove(file_path)
#                     deleted_files.append(filename)

#                     # پاک کردن hash مربوطه
#                     hash_path = file_path + ".hash"
#                     if os.path.exists(hash_path):
#                         os.remove(hash_path)
#                         deleted_files.append(filename + ".hash")
#                 except Exception as e:
#                     errors.append({filename: str(e)})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error while scanning directory: {e}")

#     return JSONResponse(
#         content={
#             "status": "success",
#             "deleted_files": deleted_files,
#             "errors": errors,
#             "total_deleted": len(deleted_files),
#         }
#     )

import os
import shutil
import uuid
import hashlib
from datetime import datetime
from typing import List
from app.dependencies.db import get_db
from sqlalchemy.orm import Session


from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.models.user import User
from app.dependencies.auth import get_current_user

from app.iot.mqtt.client import mqtt_publish
from app.core.config import settings
from app.crud.device import get_all_active_multimedia_device_codes

from urllib.parse import quote


router = APIRouter()
MEDIA_DIR = "media"


def calculate_file_hash(file) -> str:
    """Calculate SHA256 hash of uploaded file"""
    hasher = hashlib.sha256()
    file.file.seek(0)
    while chunk := file.file.read(8192):
        hasher.update(chunk)
    file.file.seek(0)
    return hasher.hexdigest()

def notify_device_download(device_code: str, filename: str):
    print(f"\n{'='*80}")
    print(f"[NOTIFY_DEVICE_DOWNLOAD] شروع تابع")
    print(f"[NOTIFY_DEVICE_DOWNLOAD] device_code: {device_code}")
    print(f"[NOTIFY_DEVICE_DOWNLOAD] filename: {filename}")
    print(f"[NOTIFY_DEVICE_DOWNLOAD] filename type: {type(filename)}")
    
    try:
        encoded_filename = quote(filename)
        print(f"[NOTIFY_DEVICE_DOWNLOAD] encoded_filename: {encoded_filename}")
        
        url = f"{settings.SERVER_HOST}/media/{encoded_filename}"
        print(f"[NOTIFY_DEVICE_DOWNLOAD] SERVER_HOST: {settings.SERVER_HOST}")
        print(f"[NOTIFY_DEVICE_DOWNLOAD] URL ساخته شده: {url}")
        
        payload = {
            "type": "MEDIA",
            "action": "download",
            "url": url,
            "file": filename
        }
        print(f"[NOTIFY_DEVICE_DOWNLOAD] payload: {payload}")
        
        topic = f"greeni/device/{device_code}/command"
        print(f"[NOTIFY_DEVICE_DOWNLOAD] MQTT topic: {topic}")
        
        mqtt_publish(topic, payload)
        print(f"[NOTIFY_DEVICE_DOWNLOAD] ✅ MQTT publish موفق")
        print(f"[NOTIFY_DEVICE_DOWNLOAD] پیام ارسال شد به دستگاه: {device_code}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"[NOTIFY_DEVICE_DOWNLOAD] ❌ خطا در notify_device_download:")
        print(f"[NOTIFY_DEVICE_DOWNLOAD] خطا: {str(e)}")
        print(f"[NOTIFY_DEVICE_DOWNLOAD] نوع خطا: {type(e).__name__}")
        import traceback
        print(f"[NOTIFY_DEVICE_DOWNLOAD] Traceback:\n{traceback.format_exc()}")
        print(f"{'='*80}\n")


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"\n{'='*80}")
    print(f"[UPLOAD] شروع آپلود فایل‌ها")
    print(f"[UPLOAD] تعداد فایل‌ها: {len(files)}")
    print(f"[UPLOAD] کاربر: {current_user}")
    
    os.makedirs(MEDIA_DIR, exist_ok=True, mode=0o777)
    print(f"[UPLOAD] MEDIA_DIR آماده شد: {MEDIA_DIR}")
    
    results = []

    for idx, file in enumerate(files):
        print(f"\n[UPLOAD] ==================== فایل {idx + 1} ====================")
        print(f"[UPLOAD] نام فایل: {file.filename}")
        print(f"[UPLOAD] سایز فایل: {file.size}")
        print(f"[UPLOAD] نوع فایل: {file.content_type}")
        
        try:
            file_hash = calculate_file_hash(file)
            print(f"[UPLOAD] هش محاسبه شد: {file_hash}")

            # چک کن فایل مشابه قبلاً وجود داره یا نه
            print(f"[UPLOAD] درحال جستجوی فایل‌های تکراری...")
            duplicate_found = False
            
            for existing in os.listdir(MEDIA_DIR):
                if existing.endswith(".hash"):
                    with open(os.path.join(MEDIA_DIR, existing), "r") as f:
                        existing_hash = f.read().strip()
                        if existing_hash == file_hash:
                            # همون فایل پیدا شد
                            stored_filename = existing.replace(".hash", "")
                            print(f"[UPLOAD] ✅ فایل تکراری پیدا شد: {stored_filename}")
                            duplicate_found = True
                            results.append({
                                "original_filename": file.filename,
                                "stored_filename": stored_filename,
                                "url": f"/media/{stored_filename}",
                                "duplicate": True,
                            })
                            break
            
            if not duplicate_found:
                # فایل جدید رو ذخیره کن
                print(f"[UPLOAD] فایل جدید است، درحال ذخیره...")
                
                unique_id = str(uuid.uuid4())
                date_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                safe_name = file.filename.replace(" ", "_")
                stored_filename = f"{date_str}_{unique_id}_{safe_name}"
                file_path = os.path.join(MEDIA_DIR, stored_filename)

                print(f"[UPLOAD] نام ذخیره‌شده: {stored_filename}")
                print(f"[UPLOAD] مسیر کامل: {file_path}")

                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                print(f"[UPLOAD] ✅ فایل در دیسک ذخیره شد")

                # هش رو ذخیره کن
                with open(file_path + ".hash", "w") as f:
                    f.write(file_hash)
                print(f"[UPLOAD] ✅ فایل هش ذخیره شد")

                os.chmod(file_path, 0o666)
                print(f"[UPLOAD] ✅ permissions تنظیم شدند")

                results.append({
                    "original_filename": file.filename,
                    "stored_filename": stored_filename,
                    "url": f"/media/{stored_filename}",
                    "duplicate": False,
                })
            
            print(f"[UPLOAD] فایل {idx + 1} آپلود موفق")
            
        except Exception as e:
            print(f"[UPLOAD] ❌ خطا در آپلود فایل {idx + 1}:")
            print(f"[UPLOAD] خطا: {str(e)}")
            print(f"[UPLOAD] نوع خطا: {type(e).__name__}")
            import traceback
            print(f"[UPLOAD] Traceback:\n{traceback.format_exc()}")

    # درحال ارسال دستور دانلود به دستگاه‌ها
    print(f"\n[UPLOAD] ==================== ارسال دستور دانلود ====================")
    print(f"[UPLOAD] درحال دریافت لیست دستگاه‌های فعال...")
    
    try:
        active_devices = get_all_active_multimedia_device_codes(db)
        print(f"[UPLOAD] تعداد دستگاه‌های فعال: {len(active_devices) if active_devices else 0}")
        print(f"[UPLOAD] کدهای دستگاه: {active_devices}")
        
        for stored_result in results:
            stored_filename = stored_result.get("stored_filename")
            is_duplicate = stored_result.get("duplicate")
            
            print(f"\n[UPLOAD] درحال پردازش: {stored_filename} (تکراری: {is_duplicate})")
            
            # فقط برای فایل‌های جدید (نه تکراری)
            if not is_duplicate:
                if active_devices:
                    for device_code in active_devices:
                        print(f"[UPLOAD] ارسال دستور به دستگاه: {device_code}")
                        notify_device_download(device_code, stored_filename)
                else:
                    print(f"[UPLOAD] ⚠️ هیچ دستگاه فعالی وجود ندارد")
            else:
                print(f"[UPLOAD] ⏭️ فایل تکراری است، دستور دانلود ارسال نمی‌شود")
                
    except Exception as e:
        print(f"[UPLOAD] ❌ خطا در ارسال دستور‌های دانلود:")
        print(f"[UPLOAD] خطا: {str(e)}")
        print(f"[UPLOAD] نوع خطا: {type(e).__name__}")
        import traceback
        print(f"[UPLOAD] Traceback:\n{traceback.format_exc()}")

    print(f"\n[UPLOAD] ==================== پایان آپلود ====================")
    print(f"[UPLOAD] نتیجه نهایی:")
    print(f"[UPLOAD] تعداد نتایج: {len(results)}")
    print(f"[UPLOAD] {results}")
    print(f"{'='*80}\n")

    return {"uploaded": results}


@router.delete("/delete/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    print(f"\n{'='*80}")
    print(f"[DELETE] درخواست حذف فایل")
    print(f"[DELETE] نام فایل: {filename}")
    print(f"[DELETE] کاربر: {current_user}")
    
    file_path = os.path.join(MEDIA_DIR, filename)
    hash_path = file_path + ".hash"
    
    print(f"[DELETE] مسیر فایل: {file_path}")
    print(f"[DELETE] مسیر هش: {hash_path}")
    print(f"[DELETE] آیا فایل موجود است: {os.path.exists(file_path)}")

    if not os.path.exists(file_path):
        print(f"[DELETE] ❌ فایل پیدا نشد")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(file_path)
        print(f"[DELETE] ✅ فایل حذف شد")
        
    except Exception as e:
        print(f"[DELETE] ❌ خطا در حذف فایل: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

    print(f"[DELETE] ✅ عملیات موفق")
    print(f"{'='*80}\n")
    
    return JSONResponse(content={"deleted": filename, "status": "success"})

@router.delete("/delete-all")
async def delete_all_files(
    current_user: User = Depends(get_current_user),
):
    print(f"\n{'='*80}")
    print(f"[DELETE_ALL] درخواست حذف تمام فایل‌ها")
    print(f"[DELETE_ALL] کاربر: {current_user}")
    
    if not os.path.exists(MEDIA_DIR):
        print(f"[DELETE_ALL] ❌ دایرکتوری پیدا نشد")
        raise HTTPException(status_code=404, detail="Media directory not found")

    deleted_files = []
    errors = []

    try:
        files_in_dir = os.listdir(MEDIA_DIR)
        print(f"[DELETE_ALL] فایل‌های موجود: {files_in_dir}")
        
        for filename in files_in_dir:
            file_path = os.path.join(MEDIA_DIR, filename)

            if os.path.isfile(file_path) and not filename.endswith(".hash"):
                print(f"[DELETE_ALL] حذف: {filename}")
                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                    print(f"[DELETE_ALL] ✅ {filename} حذف شد")
                    
                except Exception as e:
                    print(f"[DELETE_ALL] ❌ خطا در حذف {filename}: {str(e)}")
                    errors.append({filename: str(e)})
                    
    except Exception as e:
        print(f"[DELETE_ALL] ❌ خطا در اسکن دایرکتوری: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while scanning directory: {e}")

    print(f"[DELETE_ALL] ✅ عملیات موفق")
    print(f"[DELETE_ALL] حذف‌شده‌ها: {len(deleted_files)}")
    print(f"{'='*80}\n")
    
    return JSONResponse(
        content={
            "status": "success",
            "deleted_files": deleted_files,
            "errors": errors,
            "total_deleted": len(deleted_files),
        }
    )


@router.delete("/delete-all-hash")
async def delete_all_files_with_hash(
    current_user: User = Depends(get_current_user),
):
    print(f"\n{'='*80}")
    print(f"[DELETE_ALL_HASH] درخواست حذف تمام فایل‌ها و هش‌ها")
    print(f"[DELETE_ALL_HASH] کاربر: {current_user}")
    
    if not os.path.exists(MEDIA_DIR):
        print(f"[DELETE_ALL_HASH] ❌ دایرکتوری پیدا نشد")
        raise HTTPException(status_code=404, detail="Media directory not found")

    deleted_files = []
    errors = []

    try:
        files_in_dir = os.listdir(MEDIA_DIR)
        print(f"[DELETE_ALL_HASH] فایل‌های موجود: {files_in_dir}")
        
        for filename in files_in_dir:
            file_path = os.path.join(MEDIA_DIR, filename)

            if os.path.isfile(file_path):
                print(f"[DELETE_ALL_HASH] حذف: {filename}")
                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                    print(f"[DELETE_ALL_HASH] ✅ {filename} حذف شد")

                    hash_path = file_path + ".hash"
                    if os.path.exists(hash_path):
                        os.remove(hash_path)
                        deleted_files.append(filename + ".hash")
                        print(f"[DELETE_ALL_HASH] ✅ {filename}.hash حذف شد")
                        
                except Exception as e:
                    print(f"[DELETE_ALL_HASH] ❌ خطا در حذف {filename}: {str(e)}")
                    errors.append({filename: str(e)})
                    
    except Exception as e:
        print(f"[DELETE_ALL_HASH] ❌ خطا در اسکن دایرکتوری: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while scanning directory: {e}")

    print(f"[DELETE_ALL_HASH] ✅ عملیات موفق")
    print(f"[DELETE_ALL_HASH] حذف‌شده‌ها: {len(deleted_files)}")
    print(f"{'='*80}\n")
    
    return JSONResponse(
        content={
            "status": "success",
            "deleted_files": deleted_files,
            "errors": errors,
            "total_deleted": len(deleted_files),
        }
    )