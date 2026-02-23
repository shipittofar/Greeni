from .base import BaseCommandExecutor
from app.iot.mqtt.client import mqtt_publish
from app.iot.mqtt.topics import get_commands_topic
from loguru import logger


class ActuatorCommandExecutor(BaseCommandExecutor):
    async def execute(self):
        device_id = self.command.get("device")
        action = self.command.get("action")
        actuator_id = self.command.get("actuator_id")

        if not device_id:
            logger.warning("[ActuatorExecutor] Missing device_id in command payload")
            return

        topic = get_commands_topic(str(device_id))
        payload = {
            "uuid": self.command.get("uuid"),        # correlation ID for status tracking
            "type": "ACTUATOR",
            "target": actuator_id,
            "action": action,
            "payload": self.command.get("payload"),  # forward any extra params as-is
        }

        success = mqtt_publish(topic, payload, device_id=str(device_id))
        if not success:
            logger.error(
                f"[ActuatorExecutor] Failed to publish actuator command "
                f"uuid={payload['uuid']} to device {device_id}"
            )
