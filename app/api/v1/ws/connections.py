# app/api/v1/ws/connections.py
from typing import List, Dict
from starlette.websockets import WebSocket

# کانکشن‌های فعال بر اساس نوع
connections: Dict[str, List[WebSocket]] = {
    "media": [],
    "system_info": [],
    "devices": [],
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
