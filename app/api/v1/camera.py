from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.camera.schemas.camera import (
    CameraCreate, CameraUpdate, CameraResponse, CameraListResponse, 
    PTZMove, CameraApprovePending, CameraPendingResponse, CameraPendingListResponse,
    CameraPendingCountResponse
)
from app.camera.crud.camera import camera_crud, ptz_crud
from app.camera.manager.camera_manager import get_camera_manager
from app.camera.manager.streaming import get_streaming_manager
from app.camera.utils.camera_utils import CameraStreamingService
from app.models.user import User
from app.schemas.common import BaseAPIResponse


router = APIRouter(tags=["Cameras"])

# ============= PENDING CAMERAS ENDPOINTS =============

@router.get("/pending", response_model=BaseAPIResponse[CameraPendingListResponse])
def get_pending_cameras(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending cameras (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can view pending cameras")
    
    pending_cameras = camera_crud.get_pending_cameras(db)
    return BaseAPIResponse(
        result=CameraPendingListResponse(
            total=len(pending_cameras),
            pending_cameras=pending_cameras
        )
    )

@router.post("/pending/{camera_id}/approve", response_model=BaseAPIResponse[CameraResponse])
def approve_pending_camera(
    camera_id: int,
    approval: CameraApprovePending,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject a pending camera (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can approve cameras")
    
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if not camera.is_pending:
        raise HTTPException(status_code=400, detail="Camera is not pending")
    
    if approval.approved:
        camera = camera_crud.activate_camera(db, camera_id)
        return BaseAPIResponse(
            result=camera,
            message="Camera approved and activated successfully"
        )
    else:
        success = camera_crud.reject_pending_camera(db, camera_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reject camera")
        
        return BaseAPIResponse(
            result=None,
            message=f"Camera rejected and deleted. Reason: {approval.notes or 'No reason provided'}"
        )

@router.get("/pending/count", response_model=BaseAPIResponse[dict])
def get_pending_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of pending cameras (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can view pending cameras")
    
    count = camera_crud.get_pending_count(db)
    return BaseAPIResponse(result={"pending_count": count})

# ============= CAMERA LIFECYCLE ENDPOINTS =============

@router.post("/{camera_id}/activate", response_model=BaseAPIResponse[CameraResponse])
def activate_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually activate a camera (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can activate cameras")
    
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera = camera_crud.activate_camera(db, camera_id)
    return BaseAPIResponse(result=camera, message="Camera activated successfully")

@router.post("/{camera_id}/deactivate", response_model=BaseAPIResponse[CameraResponse])
def deactivate_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually deactivate a camera (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can deactivate cameras")
    
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera = camera_crud.deactivate_camera(db, camera_id)
    return BaseAPIResponse(result=camera, message="Camera deactivated successfully")

# ============= STANDARD CRUD ENDPOINTS =============

@router.get("/", response_model=BaseAPIResponse[List[CameraResponse]])
async def get_all_camera(
    only_active: bool = Query(False, description="Only return active cameras"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all cameras except pending ones, optional filter for active"""

    cameras = camera_crud.get_non_pending(
        db=db,
        only_active=only_active,
        skip=skip,
        limit=limit
    )

    return BaseAPIResponse(result=cameras)


@router.post("/", response_model=BaseAPIResponse[CameraResponse])
async def create_camera(
    camera_in: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check device_id
    if not camera_in.device_id:
        raise HTTPException(
            status_code=400,
            detail="device_id is required for creating a camera."
        )

    camera = camera_crud.create(db, camera_in)
    return BaseAPIResponse(
        result=camera,
        message="Camera created in pending state. Awaiting admin approval."
    )


@router.get("/device/{device_id}", response_model=CameraListResponse)
async def get_cameras(
    device_id: int,
    only_active: bool = Query(True, description="Only return active cameras"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all cameras for a specific device"""
    if only_active:
        cameras = db.query(camera_crud.model).filter(
            and_(
                camera_crud.model.device_id == device_id,
                camera_crud.model.is_active == True
            )
        ).offset(skip).limit(limit).all()
    else:
        cameras = camera_crud.get_by_device(db, device_id)
    
    return CameraListResponse(total=len(cameras), cameras=cameras)

@router.get("/{camera_id}", response_model=BaseAPIResponse[CameraResponse])
async def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get camera details by ID"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera_data = CameraResponse.from_orm(camera)
    return BaseAPIResponse(result=camera_data)

@router.put("/{camera_id}", response_model=BaseAPIResponse[CameraResponse])
async def update_camera(
    camera_id: int,
    camera_in: CameraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update camera configuration"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera = camera_crud.update(db, camera, camera_in)
    return BaseAPIResponse(result=camera, message="Camera updated successfully")

@router.delete("/{camera_id}", response_model=BaseAPIResponse[dict])
async def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a camera permanently"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera_crud.remove(db, camera_id)
    return BaseAPIResponse(result={}, message="Camera deleted successfully")

# ============= STREAMING ENDPOINTS =============

@router.get("/{camera_id}/frame")
async def get_frame(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single frame from camera"""
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if not camera.is_active:
        raise HTTPException(status_code=400, detail="Camera is not active")
    
    # Get connected camera (auto-connects if needed)
    camera_info = await CameraStreamingService.get_connected_camera(db, camera_id)
    if not camera_info:
        raise HTTPException(status_code=400, detail="Failed to connect camera")
    
    manager = get_camera_manager()
    frame = await manager.get_frame(camera_id)
    
    if not frame:
        raise HTTPException(status_code=400, detail="Failed to get frame from camera")
    
    return Response(content=frame, media_type="image/jpeg")

@router.get("/{camera_id}/stream/mjpeg")
async def stream_mjpeg(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stream camera as MJPEG (supports USB, IP, RTSP)
    
    Real-time MJPEG stream for all camera types.
    Automatically connects camera if not already connected.
    """
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if not camera.is_active:
        raise HTTPException(status_code=400, detail="Camera is not active")
    
    # Get connected camera (auto-connects if needed)
    camera_info = await CameraStreamingService.get_connected_camera(db, camera_id)
    if not camera_info:
        raise HTTPException(status_code=400, detail="Failed to connect camera. Check connection settings.")
    
    cap = camera_info['cap']
    streaming = get_streaming_manager()
    streaming.streams[camera_id] = {'active': True, 'type': camera.type.value}
    
    # Use streaming quality from camera config
    quality_map = {'low': 60, 'medium': 80, 'high': 95}
    quality = quality_map.get(camera.streaming_quality, 80)
    
    return Response(
        content=streaming.start_mjpeg_stream(camera_id, cap, quality=quality),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.post("/{camera_id}/stream/hls/start")
async def start_hls_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Start HLS streaming (IP/RTSP only)
    
    Returns playlist URL for HTTP Live Streaming.
    Only works with IP and RTSP cameras.
    """
    camera = camera_crud.get(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if not camera.is_active:
        raise HTTPException(status_code=400, detail="Camera is not active")
    
    # HLS only supports IP/RTSP cameras
    if camera.type.value not in ['ip', 'rtsp']:
        raise HTTPException(
            status_code=400, 
            detail=f"HLS not supported for {camera.type.value} cameras. Use MJPEG instead."
        )
    
    # Get connected camera
    camera_info = await CameraStreamingService.get_connected_camera(db, camera_id)
    if not camera_info:
        raise HTTPException(status_code=400, detail="Failed to connect camera")
    
    streaming = get_streaming_manager()
    rtsp_url = camera_info.get('url')
    
    if not rtsp_url:
        raise HTTPException(status_code=400, detail="Invalid camera URL")
    
    playlist = await streaming.start_hls_stream(camera_id, rtsp_url)
    
    if not playlist:
        raise HTTPException(status_code=400, detail="Failed to start HLS stream")
    
    return BaseAPIResponse(
        result={"playlist_url": playlist},
        message="HLS stream started successfully"
    )

@router.post("/{camera_id}/stream/hls/stop")
async def stop_hls_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop HLS streaming for a camera"""
    streaming = get_streaming_manager()
    await streaming.stop_stream(camera_id)
    return BaseAPIResponse(result={}, message="Stream stopped successfully")

@router.post("/{camera_id}/stream/stop")
async def stop_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop all streaming for a camera"""
    streaming = get_streaming_manager()
    await streaming.stop_stream(camera_id)
    
    # Optionally disconnect camera
    # await CameraStreamingService.disconnect_camera(camera_id)
    
    return BaseAPIResponse(result={}, message="All streams stopped")