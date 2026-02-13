import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import cv2
import subprocess
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class CameraManager:
    """Main camera management class"""
    
    def __init__(self):
        self.active_streams: Dict[int, Any] = {}
        self.camera_connections: Dict[int, Any] = {}
    
    async def connect_camera(self, camera_id: int, camera_data: Dict) -> bool:
        """
        Connect to camera (IP or USB)
        Returns True if successful
        """
        try:
            camera_type = camera_data.get('type')
            
            if camera_type == 'ip' or camera_type == 'rtsp':
                return await self._connect_ip_camera(camera_id, camera_data)
            elif camera_type == 'usb':
                return await self._connect_usb_camera(camera_id, camera_data)
            else:
                logger.error(f"Unknown camera type: {camera_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting camera {camera_id}: {str(e)}")
            return False
    
    async def _connect_ip_camera(self, camera_id: int, camera_data: Dict) -> bool:
        """Connect to IP camera via RTSP"""
        try:
            url = camera_data.get('url')
            username = camera_data.get('username')
            password = camera_data.get('password')
            port = camera_data.get('port', 554)
            
            # Build RTSP URL
            if not url.startswith('rtsp://'):
                if username and password:
                    rtsp_url = f"rtsp://{username}:{password}@{url}:{port}/stream"
                else:
                    rtsp_url = f"rtsp://{url}:{port}/stream"
            else:
                rtsp_url = url
            
            # Test connection
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                logger.error(f"Failed to connect to IP camera {camera_id}")
                return False
            
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            self.camera_connections[camera_id] = {
                'cap': cap,
                'url': rtsp_url,
                'width': width,
                'height': height,
                'fps': fps,
                'connected_at': datetime.utcnow()
            }
            
            logger.info(f"Successfully connected to IP camera {camera_id} ({width}x{height}@{fps}fps)")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting IP camera {camera_id}: {str(e)}")
            return False
    
    async def _connect_usb_camera(self, camera_id: int, camera_data: Dict) -> bool:
        """Connect to USB camera"""
        try:
            url = camera_data.get('url')  # Device path like /dev/video0
            
            # Parse device ID from path
            device_id = int(url.split('video')[-1])
            
            cap = cv2.VideoCapture(device_id)
            if not cap.isOpened():
                logger.error(f"Failed to connect to USB camera {camera_id}")
                return False
            
            # Set resolution and FPS
            fps = camera_data.get('fps', 30)
            width = camera_data.get('resolution_width', 1280)
            height = camera_data.get('resolution_height', 720)
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)
            
            # Verify settings
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            self.camera_connections[camera_id] = {
                'cap': cap,
                'device_id': device_id,
                'width': actual_width,
                'height': actual_height,
                'fps': actual_fps,
                'connected_at': datetime.utcnow()
            }
            
            logger.info(f"Successfully connected to USB camera {camera_id} ({actual_width}x{actual_height}@{actual_fps}fps)")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting USB camera {camera_id}: {str(e)}")
            return False
    
    async def disconnect_camera(self, camera_id: int) -> bool:
        """Disconnect from camera"""
        try:
            if camera_id in self.camera_connections:
                cap = self.camera_connections[camera_id].get('cap')
                if cap:
                    cap.release()
                del self.camera_connections[camera_id]
            
            # Stop streaming if active
            if camera_id in self.active_streams:
                await self.stop_stream(camera_id)
            
            logger.info(f"Disconnected from camera {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting camera {camera_id}: {str(e)}")
            return False
    
    async def get_frame(self, camera_id: int) -> Optional[bytes]:
        """Get single frame from camera as JPEG"""
        try:
            if camera_id not in self.camera_connections:
                return None
            
            cap = self.camera_connections[camera_id]['cap']
            ret, frame = cap.read()
            
            if not ret:
                logger.warning(f"Failed to read frame from camera {camera_id}")
                return None
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                return None
            
            return buffer.tobytes()
            
        except Exception as e:
            logger.error(f"Error getting frame from camera {camera_id}: {str(e)}")
            return None
    
    async def get_camera_info(self, camera_id: int) -> Optional[Dict]:
        """Get camera connection info"""
        if camera_id in self.camera_connections:
            return self.camera_connections[camera_id]
        return None


# Singleton instance
_camera_manager = None

def get_camera_manager() -> CameraManager:
    global _camera_manager
    if _camera_manager is None:
        _camera_manager = CameraManager()
    return _camera_manager