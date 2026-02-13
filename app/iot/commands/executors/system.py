from .base import BaseCommandExecutor
import psutil
import platform
import socket
import os
import json

class SystemCommandExecutor(BaseCommandExecutor):
    async def execute(self):
        command_type = self.command.get("subtype")

        if command_type == "REBOOT":
            os.system("sudo reboot")

        elif command_type == "GET_INFO":
            info = self.get_device_info()
            await self.mqtt_client.publish(
                topic="devices/info/response",
                payload=json.dumps({
                    "device_id": self.device_id,
                    "info": info
                })
            )

    def get_device_info(self):
        return {
            "hostname": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "cpu_percent": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "platform": platform.platform(),
            "temperature": self.get_temp()
        }

    def get_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read()) / 1000.0
            return temp
        except:
            return None
