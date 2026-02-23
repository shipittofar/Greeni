from .base import BaseCommandExecutor
from app.iot.mqtt.client import mqtt_publish
from app.iot.mqtt.topics import get_command_topic
from loguru import logger


class ActuatorCommandExecutor(BaseCommandExecutor):
    async def execute(self):
        device_id = self.command.get("device")
        action = self.command.get("action")
        actuator_id = self.command.get("actuator_id")

        if not device_id:
            logger.warning("[ActuatorExecutor] Missing device_id in command payload")
            return

        topic = get_command_topic(str(device_id))
        payload = {
            "type": "ACTUATOR",
            "target": actuator_id,
            "action": action,
        }

        success = mqtt_publish(topic, payload, device_id=str(device_id))
        if not success:
            logger.error(f"[ActuatorExecutor] Failed to publish actuator command to device {device_id}")
