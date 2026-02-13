from app.iot.mqtt.client import mqtt_publish
from app.schemas.command import CommandPublic

def publish_command(command: CommandPublic):
    """
    ارسال فرمان به دیوایس از طریق MQTT
    """
    if not command.device_id:
        # اگر دیوایس اختصاص داده نشده بود
        return

    topic = f"greeni/device/{command.device_id}/commands"
    payload = {
        "uuid": str(command.uuid),
        "command": command.command,
        "type": "ACTUATOR",
        "payload": command.payload or {},
        "status": command.status,
    }
    mqtt_publish(topic, payload, device_id=str(command.device_id))
