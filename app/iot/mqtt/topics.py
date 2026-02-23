# app/iot/mqtt/topics.py
TOPIC_PREFIX = "greeni/device/"


def get_command_topic(device_id: str) -> str:
    """Downlink: server → device  (legacy single-command channel)"""
    return f"{TOPIC_PREFIX}{device_id}/command"


def get_commands_topic(device_id: str) -> str:
    """Downlink: server → device  (command queue channel used by publisher)"""
    return f"{TOPIC_PREFIX}{device_id}/commands"


def get_command_status_topic(device_id: str) -> str:
    """Uplink: device → server  (device reports command execution result)"""
    return f"{TOPIC_PREFIX}{device_id}/commands/status"


def get_data_topic(device_id: str) -> str:
    """Uplink: device → server  (sensor / telemetry data)"""
    return f"{TOPIC_PREFIX}{device_id}/data"


def get_media_list_response_topic(device_id: str) -> str:
    """Uplink: device → server  (media file list response)"""
    return f"{TOPIC_PREFIX}{device_id}/media/media_list"


def get_system_info_topic(device_id: str) -> str:
    """Uplink: device → server  (system info response)"""
    return f"{TOPIC_PREFIX}{device_id}/system/info"
