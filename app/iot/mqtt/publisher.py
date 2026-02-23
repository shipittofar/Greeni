# app/iot/mqtt/publisher.py
from app.iot.mqtt.client import mqtt_publish
from app.iot.mqtt.topics import get_commands_topic
from app.schemas.command import CommandPublic
from loguru import logger


def publish_command(command: CommandPublic) -> bool:
    """
    Publish a command to the device over MQTT.
    Returns True if the message was queued successfully, False otherwise.
    """
    if not command.device_id:
        logger.warning("[Publisher] publish_command called with no device_id — skipped")
        return False

    topic = get_commands_topic(str(command.device_id))
    payload = {
        "uuid": str(command.uuid),
        "command": command.command,
        "type": "ACTUATOR",
        "payload": command.payload or {},
        "status": command.status,
    }

    success = mqtt_publish(topic, payload, device_id=str(command.device_id))
    if not success:
        logger.error(f"[Publisher] Failed to publish command uuid={command.uuid} to device {command.device_id}")
    return success
