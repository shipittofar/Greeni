from .base import BaseCommandExecutor
from app.iot.mqtt.client import mqtt_publish
from app.iot.mqtt.topics import get_system_info_topic
from loguru import logger
import psutil
import platform
import socket
import os


class SystemCommandExecutor(BaseCommandExecutor):
    async def execute(self):
        device_id = self.command.get("device")
        subtype = self.command.get("subtype")

        if subtype == "REBOOT":
            logger.warning(f"[SystemExecutor] REBOOT requested for device {device_id}")
            os.system("sudo reboot")

        elif subtype == "GET_INFO":
            if not device_id:
                logger.warning("[SystemExecutor] GET_INFO missing device_id")
                return

            info = self._get_device_info()
            topic = get_system_info_topic(str(device_id))
            payload = {"device_id": device_id, "info": info}

            success = mqtt_publish(topic, payload, device_id=str(device_id))
            if not success:
                logger.error(f"[SystemExecutor] Failed to publish system info for device {device_id}")

        else:
            logger.warning(f"[SystemExecutor] Unknown subtype: {subtype}")

    def _get_device_info(self) -> dict:
        return {
            "hostname": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "platform": platform.platform(),
            "temperature": self._get_temp(),
        }

    def _get_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return int(f.read()) / 1000.0
        except Exception:
            return None
