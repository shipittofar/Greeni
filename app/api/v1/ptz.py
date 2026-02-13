from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.camera.schemas.camera import PTZMove, PTZPreset, PTZControlResponse
from app.camera.crud.camera import ptz_crud, camera_crud
from app.camera.manager.ptz_controller import get_ptz_controller, PTZDirection
from app.models.user import User

router = APIRouter()

@router.post("/{camera_id}/initialize")
async def initialize_ptz(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize PTZ for camera"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if not camera.has_ptz:
        raise HTTPException(status_code=400, detail="Camera does not support PTZ")
    
    controller = get_ptz_controller()
    
    # Extract IP from URL
    ip_address = camera.url.split('://')[1].split(':')[0] if '://' in camera.url else camera.url
    
    success = await controller.initialize_ptz(
        camera_id,
        ip_address,
        camera.username or "",
        camera.password or "",
        camera.port or 80
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to initialize PTZ")
    
    return {"message": "PTZ initialized successfully"}

@router.post("/{camera_id}/move")
async def move_camera(
    camera_id: int,
    move: PTZMove,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Move camera in direction"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    controller = get_ptz_controller()
    
    try:
        direction = PTZDirection(move.direction)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid direction")
    
    # Run movement in background
    background_tasks.add_task(
        controller.continuous_move,
        camera_id,
        direction,
        move.speed,
        move.duration
    )
    
    return {"message": f"Moving {move.direction}"}

@router.post("/{camera_id}/absolute-move")
async def absolute_move(
    camera_id: int,
    pan: float = 0.5,
    tilt: float = 0.5,
    speed: float = 0.5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Move to absolute position"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Validate ranges
    if not (0 <= pan <= 1 and 0 <= tilt <= 1 and 0 <= speed <= 1):
        raise HTTPException(status_code=400, detail="Invalid pan/tilt/speed values (must be 0-1)")
    
    controller = get_ptz_controller()
    success = await controller.pan_tilt(camera_id, pan, tilt, speed)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to move camera")
    
    # Update position in DB
    ptz_data = {
        'pan_position': pan,
        'tilt_position': tilt,
        'pan_speed': speed,
        'tilt_speed': speed
    }
    ptz_crud.create_or_update(db, camera_id, ptz_data)
    
    return {"message": "Camera moved", "pan": pan, "tilt": tilt}

@router.post("/{camera_id}/zoom")
async def zoom_camera(
    camera_id: int,
    zoom: float = 0.5,
    speed: float = 0.5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Zoom camera"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if not (-1 <= zoom <= 1 and 0 <= speed <= 1):
        raise HTTPException(status_code=400, detail="Invalid zoom/speed values")
    
    controller = get_ptz_controller()
    success = await controller.zoom(camera_id, zoom, speed)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to zoom")
    
    # Update position in DB
    ptz_data = {'zoom_position': (zoom + 1) / 2, 'zoom_speed': speed}
    ptz_crud.create_or_update(db, camera_id, ptz_data)
    
    return {"message": "Zoomed", "zoom": zoom}

@router.post("/{camera_id}/home")
async def home_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Move camera to home position"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    controller = get_ptz_controller()
    success = await controller.go_home(camera_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to go home")
    
    return {"message": "Moved to home position"}

@router.post("/{camera_id}/stop")
async def stop_movement(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop all PTZ movements"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    controller = get_ptz_controller()
    success = await controller.stop_movement(camera_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop")
    
    return {"message": "Movement stopped"}

@router.post("/{camera_id}/preset/save")
async def save_preset(
    camera_id: int,
    preset_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save current position as preset"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    controller = get_ptz_controller()
    preset_token = await controller.save_preset(camera_id, preset_name)
    
    if not preset_token:
        raise HTTPException(status_code=400, detail="Failed to save preset")
    
    return {"message": "Preset saved", "preset_token": preset_token}

@router.post("/{camera_id}/preset/load")
async def load_preset(
    camera_id: int,
    preset_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Load preset position"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    controller = get_ptz_controller()
    success = await controller.goto_preset(camera_id, preset_token)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to load preset")
    
    return {"message": "Preset loaded"}

@router.get("/{camera_id}/presets")
async def list_presets(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all presets for camera"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    presets = ptz_crud.get_presets(db, camera_id)
    return {"presets": presets}