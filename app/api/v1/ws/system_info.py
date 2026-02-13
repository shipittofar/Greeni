from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import psutil
import subprocess
import platform

router = APIRouter()

# def get_ram_type():
#     try:
#         output = subprocess.check_output(
#             "dmidecode -t memory | grep 'Type:' | grep -v 'Unknown'",
#             shell=True,
#             text=True
#         )
#         types = list(set([line.split(":")[1].strip() for line in output.splitlines()]))
#         return types[0] if types else "Unknown"
#     except Exception:
#         return "Unknown"

@router.websocket("/system-info")
async def websocket_system_info(websocket: WebSocket):
    await websocket.accept()
    # ram_type = get_ram_type()
    try:
        while True:
            processor = {
                "usage": psutil.cpu_percent(),
                "cores": psutil.cpu_count(logical=True),
                "clock": round(psutil.cpu_freq().current / 1000, 2),
                "arch": platform.architecture()[0],
            }
            virtual_mem = psutil.virtual_memory()
            machine = {
                "ramUsage": round(virtual_mem.percent),
                "ram": round(virtual_mem.total / (1024**3)),
                "ramType": "DDR4",
                "processes": len(psutil.pids())
            }
            disk = psutil.disk_usage('/')
            partitions = [p.device for p in psutil.disk_partitions() if 'rw' in p.opts]
            storage = {
                "usage": round(disk.percent),
                "total": round(disk.total / (1024**3)),
                "disks": len(partitions),
                "swap": round(psutil.swap_memory().total / (1024**3))
            }

            await websocket.send_json({
                "processor": processor,
                "machine": machine,
                "storage": storage
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("Client disconnected")
