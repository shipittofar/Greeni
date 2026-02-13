# # app/api/v1/ws/media_ws.py

import json
from fastapi import APIRouter, WebSocket
from app.iot.mqtt.client import mqtt_publish
from app.api.v1.ws.connections import add_connection, remove_connection
from app.core.config import settings

router = APIRouter()

@router.websocket("/media")
async def media_ws(websocket: WebSocket):
    print(f"\n{'='*80}")
    print(f"[WS] تلاش برای پذیرش WebSocket...")
    
    await websocket.accept()
    add_connection("media", websocket)
    
    print(f"[WS] ✅ Media WebSocket متصل شد")
    print(f"[WS] CLIENT_IP: {websocket.client}")
    print(f"{'='*80}\n")
    
    try:
        while True:
            print(f"[WS] درحال انتظار برای پیام...")
            msg_text = await websocket.receive_text()
            
            print(f"\n{'='*80}")
            print(f"[WS] ✅ پیام دریافت شد")
            print(f"[WS] Raw message: {msg_text}")
            
            try:
                data = json.loads(msg_text)
                print(f"[WS] JSON parse موفق")
                print(f"[WS] Data: {data}")
                
            except json.JSONDecodeError as e:
                print(f"[WS] ❌ خطا در JSON parse: {str(e)}")
                continue
            
            device_id = data.get("device_id")
            action = data.get("action")
            
            print(f"[WS] device_id: {device_id}")
            print(f"[WS] action: {action}")
            
            # Validate device_id
            if not device_id:
                print(f"[WS] ⚠️ device_id خالی است")
                await websocket.send_text(json.dumps({"error": "device_id required"}))
                continue
            
            # Validate action
            if not action:
                print(f"[WS] ⚠️ action خالی است")
                await websocket.send_text(json.dumps({"error": "action required"}))
                continue
            
            # ==================== MEDIA_LIST ====================
            if action == "media_list":
                print(f"[WS] ==================== MEDIA_LIST ====================")
                print(f"[WS] درخواست لیست رسانه‌ها")
                
                try:
                    payload = {"type": "AUDIO", "action": "media_list"}
                    topic = f"greeni/device/{device_id}/command"
                    
                    print(f"[WS] Topic: {topic}")
                    print(f"[WS] Payload: {payload}")
                    
                    mqtt_publish(topic, payload)
                    print(f"[WS] ✅ MQTT publish موفق")
                    print(f"[MQTT] Published media_list command to device {device_id}: {payload}")
                    
                except Exception as e:
                    print(f"[WS] ❌ خطا در ارسال media_list:")
                    print(f"[WS] خطا: {str(e)}")
                    import traceback
                    print(f"[WS] Traceback:\n{traceback.format_exc()}")
            
            # ==================== PLAY ====================
            elif action == "play":
                print(f"[WS] ==================== PLAY ====================")
                filename = data.get("filename")
                print(f"[WS] filename: {filename}")
                
                if not filename:
                    print(f"[WS] ⚠️ filename خالی است")
                    await websocket.send_text(json.dumps({"error": "filename required"}))
                    continue
                
                try:
                    payload = {"type": "AUDIO", "action": "play", "file": filename}
                    topic = f"greeni/device/{device_id}/command"
                    
                    print(f"[WS] Topic: {topic}")
                    print(f"[WS] Payload: {payload}")
                    
                    mqtt_publish(topic, payload)
                    print(f"[WS] ✅ MQTT publish موفق")
                    print(f"[WS] Play command for {filename} sent to device {device_id}")
                    
                except Exception as e:
                    print(f"[WS] ❌ خطا در ارسال play:")
                    print(f"[WS] خطا: {str(e)}")
                    import traceback
                    print(f"[WS] Traceback:\n{traceback.format_exc()}")
            
            # ==================== DELETE ====================
            elif action == "delete":
                print(f"[WS] ==================== DELETE ====================")
                filename = data.get("filename")
                print(f"[WS] filename: {filename}")
                
                if not filename:
                    print(f"[WS] ⚠️ filename خالی است")
                    await websocket.send_text(json.dumps({"error": "filename required"}))
                    continue
                
                try:
                    payload = {
                        "type": "MEDIA",
                        "action": "delete",
                        "file": filename
                    }
                    topic = f"greeni/device/{device_id}/command"
                    
                    print(f"[WS] Topic: {topic}")
                    print(f"[WS] Payload: {payload}")
                    
                    mqtt_publish(topic, payload)
                    print(f"[WS] ✅ MQTT publish موفق")
                    print(f"[MQTT] Published MEDIA delete command for {filename} to device {device_id}")
                    
                except Exception as e:
                    print(f"[WS] ❌ خطا در ارسال delete:")
                    print(f"[WS] خطا: {str(e)}")
                    import traceback
                    print(f"[WS] Traceback:\n{traceback.format_exc()}")
            
            # ==================== DOWNLOAD ====================
            elif action == "download":
                print(f"[WS] ==================== DOWNLOAD ====================")
                filename = data.get("filename")
                print(f"[WS] filename: {filename}")
                print(f"[WS] filename type: {type(filename)}")
                
                if not filename:
                    print(f"[WS] ⚠️ filename خالی است")
                    await websocket.send_text(json.dumps({"error": "filename required"}))
                    continue
                
                try:
                    print(f"[WS] SERVER_HOST: {settings.SERVER_HOST}")
                    print(f"[WS] SERVER_HOST type: {type(settings.SERVER_HOST)}")
                    
                    # Check if SERVER_HOST is valid
                    if not settings.SERVER_HOST:
                        print(f"[WS] ⚠️ SERVER_HOST خالی است!")
                        print(f"[WS] لطفاً SERVER_HOST را در settings تنظیم کنید")
                    
                    url = f"{settings.SERVER_HOST}/media/{filename}"
                    print(f"[WS] URL constructed: {url}")
                    print(f"[WS] URL type: {type(url)}")
                    
                    payload = {
                        "type": "MEDIA",
                        "action": "download",
                        "url": url,
                        "file": filename
                    }
                    topic = f"greeni/device/{device_id}/command"
                    
                    print(f"[WS] Topic: {topic}")
                    print(f"[WS] Payload: {payload}")
                    
                    mqtt_publish(topic, payload)
                    print(f"[WS] ✅ MQTT publish موفق")
                    print(f"[MQTT] Published MEDIA download command to device {device_id}: {payload}")
                    
                except Exception as e:
                    print(f"[WS] ❌ خطا در ارسال download:")
                    print(f"[WS] خطا: {str(e)}")
                    print(f"[WS] نوع خطا: {type(e).__name__}")
                    import traceback
                    print(f"[WS] Traceback:\n{traceback.format_exc()}")
            
            # ==================== DOWNLOAD_MULTIPLE ====================
            elif action == "download_multiple":
                print(f"[WS] ==================== DOWNLOAD_MULTIPLE ====================")
                filenames = data.get("filenames", [])
                print(f"[WS] filenames: {filenames}")
                print(f"[WS] تعداد فایل‌ها: {len(filenames)}")
                
                if not filenames:
                    print(f"[WS] ⚠️ filenames خالی است")
                    await websocket.send_text(json.dumps({"error": "filenames required"}))
                    continue
                
                try:
                    for idx, filename in enumerate(filenames):
                        print(f"\n[WS] ---- فایل {idx + 1} ----")
                        print(f"[WS] filename: {filename}")
                        
                        url = f"{settings.SERVER_HOST}/media/{filename}"
                        print(f"[WS] URL: {url}")
                        
                        payload = {
                            "type": "MEDIA",
                            "action": "download",
                            "url": url,
                            "file": filename
                        }
                        print(f"[WS] Payload: {payload}")
                        
                        topic = f"greeni/device/{device_id}/command"
                        print(f"[WS] Topic: {topic}")
                        
                        mqtt_publish(topic, payload)
                        print(f"[WS] ✅ MQTT publish موفق برای {filename}")
                        print(f"[MQTT] Published MEDIA download command for {filename}")
                    
                    print(f"\n[WS] ✅ تمام {len(filenames)} فایل ارسال شد")
                    
                except Exception as e:
                    print(f"[WS] ❌ خطا در ارسال download_multiple:")
                    print(f"[WS] خطا: {str(e)}")
                    print(f"[WS] نوع خطا: {type(e).__name__}")
                    import traceback
                    print(f"[WS] Traceback:\n{traceback.format_exc()}")
            
            # ==================== UNKNOWN ACTION ====================
            else:
                print(f"[WS] ⚠️ عملیات نامشخص: {action}")
                await websocket.send_text(json.dumps({"error": f"Unknown action: {action}"}))
            
            print(f"{'='*80}\n")
            
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"[WS] ❌ خطا در WebSocket:")
        print(f"[WS] خطا: {str(e)}")
        print(f"[WS] نوع خطا: {type(e).__name__}")
        import traceback
        print(f"[WS] Traceback:\n{traceback.format_exc()}")
        print(f"{'='*80}\n")
        
    finally:
        remove_connection("media", websocket)
        print(f"\n{'='*80}")
        print(f"[WS] ✅ Media WebSocket بسته شد")
        print(f"{'='*80}\n")




# import json
# from fastapi import APIRouter, WebSocket
# from app.iot.mqtt.client import mqtt_publish
# from app.api.v1.ws.connections import add_connection, remove_connection
# from app.core.config import settings

# router = APIRouter()

# @router.websocket("/media")
# async def media_ws(websocket: WebSocket):
#     await websocket.accept()
#     add_connection("media", websocket)
#     print("[WS] Media WebSocket connected")

#     try:
#         while True:
#             msg_text = await websocket.receive_text()
#             data = json.loads(msg_text)
#             print("[WS] Received message from client:", data)

#             device_id = data.get("device_id")
#             action = data.get("action")
#             print("action is", action)

#             if action == "media_list":
#                 payload = {"type": "AUDIO", "action": "media_list"}
#                 mqtt_publish(f"greeni/device/{device_id}/command", payload)
#                 print(f"[MQTT] Published media_list command to device {device_id}: {payload}")

#             elif action == "play":
#                 filename = data.get("filename")
#                 payload = {"type": "AUDIO", "action": "play", "file": filename}
#                 mqtt_publish(f"greeni/device/{device_id}/command", payload)
#                 print(f"[WS] Play command for {filename} sent to device {device_id}")

#             elif action == "delete":
#                 filename = data.get("filename")
#                 payload = {
#                     "type": "MEDIA",
#                     "action": "delete",
#                     "file": filename
#                 }
#                 mqtt_publish(f"greeni/device/{device_id}/command", payload)
#                 print(f"[MQTT] Published MEDIA delete command for {filename} to device {device_id}")

#             elif action == "download":
#                 filename = data.get("filename")
#                 url = f"{settings.SERVER_HOST}/media/{filename}"

#                 payload = {
#                     "type": "MEDIA",   # 🔹 تغییر دادیم
#                     "action": "download",
#                     "url": url,
#                     "file": filename
#                 }

#                 mqtt_publish(f"greeni/device/{device_id}/command", payload)
#                 print(f"[MQTT] Published MEDIA download command to device {device_id}: {payload}")

#             elif action == "download_multiple":
#                 filenames = data.get("filenames", [])
#                 for filename in filenames:
#                     url = f"{settings.SERVER_HOST}/media/{filename}"
#                     payload = {
#                         "type": "MEDIA",   # 🔹 تغییر دادیم
#                         "action": "download",
#                         "url": url,
#                         "file": filename
#                     }
#                     mqtt_publish(f"greeni/device/{device_id}/command", payload)
#                     print(f"[MQTT] Published MEDIA download command for {filename}")


#     except Exception as e:
#         print(f"❌ WebSocket error: {e}")

#     finally:
#         remove_connection("media", websocket)
#         print("[WS] Media WebSocket closed")
