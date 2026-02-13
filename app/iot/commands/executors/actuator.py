from .base import BaseCommandExecutor

class ActuatorCommandExecutor(BaseCommandExecutor):
    async def execute(self):
        device = self.command.get("device")
        action = self.command.get("action")
        actuator_id = self.command.get("actuator_id")

        # ارسال به MQTT
        topic = f"greeni/device/{device}/command"
        payload = {
            "type": "ACTUATOR",
            "target": actuator_id,
            "action": action
        }

        # import و publish کن به MQTT (از dispatcher)
        from app.iot.mqtt.client import client
        await client.publish(topic, payload)
