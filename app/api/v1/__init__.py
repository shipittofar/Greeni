from fastapi import APIRouter
from .user import router as users_router
from .role import router as roles_router
from .routes import auth
from .device import router as device_router
from .permission import router as permissions_router
from .task import router as task_router
from . import sms_provider
from . import email_provider
from . import push_provider
# from . import email_provider
from .sensor import router as sensor_router
from .tag import router as tag_router
from .command import router as command_router
from .sensor_data import router as sensor_data_router
from .ws import system_info
from .ws import system_health
from .ws import media_ws
from .ws import notifications_ws
from .ws import notifications
from .notifications import router as notifications_router
from .inapp import router as inapp_provider_router
from .media import router as media_router
from .camera import router as camera_router
from .ptz import router as ptz_router



api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(roles_router, prefix="/roles", tags=["Roles"])
api_router.include_router(permissions_router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(device_router, prefix="/devices", tags=["Devices"])
api_router.include_router(task_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(sms_provider.router, prefix="/sms-providers", tags=["Sms Providers"])
api_router.include_router(email_provider.router, prefix="/email-providers", tags=["Email Providers"])
api_router.include_router(push_provider.router, prefix="/push_provider", tags=["Push Provider"])
api_router.include_router(sensor_router, prefix="/sensors", tags=["Sensors"])
api_router.include_router(tag_router, prefix="/tags", tags=["Tags"])
api_router.include_router(system_info.router, prefix="/ws", tags=["System Info"])
api_router.include_router(system_health.router, prefix="/ws", tags=["System Health"])
api_router.include_router(media_ws.router, prefix="/ws", tags=["ws"])
api_router.include_router(notifications_ws.router, prefix="/ws", tags=["ws"])
api_router.include_router(notifications.router, prefix="/ws", tags=["ws"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(inapp_provider_router, prefix="/inapp_provider", tags=["In-App Notifications"])
api_router.include_router(command_router, prefix="/commands", tags=["Commands"])
api_router.include_router(sensor_data_router, prefix="/sensors/data", tags=["Sensor Data"])
api_router.include_router(media_router, prefix="/media", tags=["Media"])
api_router.include_router(camera_router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(ptz_router, prefix="/ptz", tags=["Camera PTZ"])

