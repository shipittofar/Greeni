# app/iot/commands/schemas.py
"""
Schemas for inbound IoT commands received over MQTT.
These describe the payload structure that *devices* send up to the server
(separate from the app/schemas/command.py which is for the REST API layer).
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel


class BaseDeviceCommand(BaseModel):
    """Every command from a device must carry a type field."""
    type: str                          # e.g. ACTUATOR | SYSTEM | SENSOR
    device: Optional[str] = None       # device_id (filled from topic if absent)
    uuid: Optional[str] = None         # optional correlation id


class ActuatorCommand(BaseDeviceCommand):
    type: str = "ACTUATOR"
    action: str                        # e.g. "on" | "off" | "set"
    actuator_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class SystemCommand(BaseDeviceCommand):
    type: str = "SYSTEM"
    subtype: str                       # "REBOOT" | "GET_INFO"


class SensorCommand(BaseDeviceCommand):
    type: str = "SENSOR"
    action: str                        # "read" | "calibrate"
    sensor_id: Optional[str] = None


class MediaCommand(BaseDeviceCommand):
    type: str = "MEDIA"
    action: str                        # "play" | "delete" | "download" | "media_list"
    file: Optional[str] = None
    url: Optional[str] = None


# Command status update sent by a device after execution
class CommandStatusUpdate(BaseModel):
    uuid: str
    status: str                        # "executed" | "failed"
    payload: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
