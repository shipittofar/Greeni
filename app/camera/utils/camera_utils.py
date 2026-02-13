import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.camera.crud.camera import camera_crud
from app.camera.manager.camera_manager import get_camera_manager

logger = logging.getLogger(__name__)


class CameraStreamingService:
    """Service for managing camera connections and streaming"""
    
    @staticmethod
    async def get_connected_camera(db: Session, camera_id: int) -> Optional[Dict]:
        """
        Get camera info and ensure it's connected.
        Automatically connects if not already connected.
        Returns camera connection info or None if fails.
        
        Returns:
            Dict with keys:
            - cap: OpenCV VideoCapture object
            - url: Connection URL
            - width/height: Frame dimensions
            - fps: Frames per second
            - connected_at: Connection timestamp
        """
        try:
            # Get camera from database
            camera = camera_crud.get(db, camera_id)
            if not camera:
                logger.error(f"Camera {camera_id} not found in database")
                return None
            
            if not camera.is_active:
                logger.error(f"Camera {camera_id} is not active")
                return None
            
            # Get camera manager
            manager = get_camera_manager()
            
            # Check if already connected
            is_connected = await manager.is_connected(camera_id)
            
            if not is_connected:
                # Prepare camera data from database
                camera_data = {
                    'type': camera.type.value,
                    'url': camera.url,
                    'username': camera.username,
                    'password': camera.password,
                    'port': camera.port,
                    'resolution_width': camera.resolution_width,
                    'resolution_height': camera.resolution_height,
                    'fps': camera.fps,
                }
                
                # Try to connect
                connected = await manager.connect_camera(camera_id, camera_data)
                if not connected:
                    logger.error(f"Failed to connect camera {camera_id}")
                    return None
            
            # Return connection info
            return await manager.get_camera_info(camera_id)
            
        except Exception as e:
            logger.error(f"Error in get_connected_camera: {str(e)}")
            return None
    
    @staticmethod
    async def disconnect_camera(camera_id: int) -> bool:
        """
        Safely disconnect camera and stop any active streams.
        
        Args:
            camera_id: ID of camera to disconnect
            
        Returns:
            True if successful, False otherwise
        """
        try:
            manager = get_camera_manager()
            return await manager.disconnect_camera(camera_id)
        except Exception as e:
            logger.error(f"Error disconnecting camera {camera_id}: {str(e)}")
            return False