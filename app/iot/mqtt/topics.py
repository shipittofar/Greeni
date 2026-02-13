# app/iot/mqtt/topics.py
DATA_TOPIC_PREFIX = "greeni/device/"
COMMAND_TOPIC_PREFIX = "greeni/device/"

def get_command_topic(device_id: str) -> str:
    return f"{COMMAND_TOPIC_PREFIX}{device_id}/command"

def get_data_topic(device_id: str) -> str:
    return f"{DATA_TOPIC_PREFIX}{device_id}/data"

def get_media_list_response_topic(device_id: str) -> str:
    return f"{DATA_TOPIC_PREFIX}{device_id}/media/media_list"
