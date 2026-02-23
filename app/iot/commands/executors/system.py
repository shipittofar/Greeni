from .base import BaseCommandExecutor
from app.iot.mqtt.client import mqtt_publish
from app.iot.mqtt.topics import get_commands_topic
from loguru import logger


# Supported system subtypes forwarded to the device
_SYSTEM_SUBTYPES = {"REBOOT", "GET_INFO", "RESTART_SERVICE"}


class SystemCommandExecutor(BaseCommandExecutor):
    """
    Server-side executor for SYSTEM commands.

    The executor does NOT run any system operations locally — it forwards
    the command to the target device over MQTT.  The device is responsible
    for executing the actual reboot / info-gathering and publishing the result
    back on its uplink topics:
        • greeni/device/{id}/system/info  — GET_INFO response
        • greeni/device/{id}/commands/status — execution ack
    """

    async def execute(self):
        device_id = self.command.get("device")
        subtype = self.command.get("subtype", "").upper()

        if not device_id:
            logger.warning("[SystemExecutor] Missing device_id — command dropped")
            return

        if subtype not in _SYSTEM_SUBTYPES:
            logger.warning(f"[SystemExecutor] Unknown subtype '{subtype}' — ignored")
            return

        topic = get_commands_topic(str(device_id))
        payload = {
            "uuid": self.command.get("uuid"),
            "type": "SYSTEM",
            "subtype": subtype,
        }

        logger.info(f"[SystemExecutor] Forwarding {subtype} to device {device_id}")
        success = mqtt_publish(topic, payload, device_id=str(device_id))
        if not success:
            logger.error(
                f"[SystemExecutor] Failed to forward {subtype} command "
                f"uuid={payload['uuid']} to device {device_id}"
            )
