# app/api/v1/ws/connections.py
from typing import List, Dict
from starlette.websockets import WebSocket

# Active WebSocket connections grouped by channel name.
# Keys must match what the MQTT handler calls via get_connections().
connections: Dict[str, List[WebSocket]] = {
    "media":   [],   # media file operations
    "command": [],   # command dispatch & status updates
    "system":  [],   # system info (CPU, memory, temp, reboot acks)
    "devices": [],   # generic device events
}

def add_connection(group: str, websocket: WebSocket):
    if group not in connections:
        connections[group] = []
    connections[group].append(websocket)

def remove_connection(group: str, websocket: WebSocket):
    if group in connections and websocket in connections[group]:
        connections[group].remove(websocket)

def get_connections(group: str) -> List[WebSocket]:
    return connections.get(group, [])
