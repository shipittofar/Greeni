import logging
from typing import Optional, Tuple
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

# Install: pip install zeep onvif-zeep-async

class PTZDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    HOME = "home"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"

class PTZController:
    """
    PTZ (Pan-Tilt-Zoom) Control
    Supports ONVIF protocol (standard for most IP cameras)
    """
    
    def __init__(self):
        self.ptz_services = {}
    
    async def initialize_ptz(
        self,
        camera_id: int,
        ip_address: str,
        username: str,
        password: str,
        port: int = 80
    ) -> bool:
        """
        Initialize PTZ service for camera
        Using ONVIF protocol
        """
        try:
            from onvif import ONVIFCamera
            
            # Create ONVIF camera instance
            camera = ONVIFCamera(
                ip_address,
                port,
                username,
                password,
                wsdl_dir='/path/to/wsdl'  # ONVIF WSDL files
            )
            
            # Get PTZ service
            ptz_service = camera.create_ptz_service()
            
            # Get camera profile (usually profile 0)
            media_service = camera.create_media_service()
            profiles = media_service.GetProfiles()
            
            if not profiles:
                logger.error(f"No profiles found for camera {camera_id}")
                return False
            
            profile_token = profiles[0].token
            
            # Get PTZ configuration
            ptz_config = ptz_service.GetNode(
                NodeToken=profile_token
            )
            
            self.ptz_services[camera_id] = {
                'camera': camera,
                'service': ptz_service,
                'profile_token': profile_token,
                'config': ptz_config,
                'initialized': True
            }
            
            logger.info(f"PTZ initialized for camera {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing PTZ for camera {camera_id}: {str(e)}")
            return False
    
    async def pan_tilt(
        self,
        camera_id: int,
        pan: float,
        tilt: float,
        speed: float = 0.5
    ) -> bool:
        """
        Pan and Tilt camera
        pan/tilt: -1 to 1 (left-right, down-up)
        speed: 0 to 1
        """
        try:
            if camera_id not in self.ptz_services:
                logger.error(f"PTZ service not initialized for camera {camera_id}")
                return False
            
            ptz_service = self.ptz_services[camera_id]['service']
            profile_token = self.ptz_services[camera_id]['profile_token']
            
            # Absolute move
            request = ptz_service.create_type('AbsoluteMove')
            request.ProfileToken = profile_token
            request.Position.PanTilt._x = pan
            request.Position.PanTilt._y = tilt
            request.Speed.PanTilt._x = speed
            request.Speed.PanTilt._y = speed
            
            ptz_service.AbsoluteMove(request)
            
            logger.info(f"Pan/Tilt command sent to camera {camera_id}: pan={pan}, tilt={tilt}")
            return True
            
        except Exception as e:
            logger.error(f"Error pan/tilt camera {camera_id}: {str(e)}")
            return False
    
    async def zoom(
        self,
        camera_id: int,
        zoom: float,
        speed: float = 0.5
    ) -> bool:
        """
        Zoom camera
        zoom: -1 (zoom out) to 1 (zoom in)
        """
        try:
            if camera_id not in self.ptz_services:
                logger.error(f"PTZ service not initialized for camera {camera_id}")
                return False
            
            ptz_service = self.ptz_services[camera_id]['service']
            profile_token = self.ptz_services[camera_id]['profile_token']
            
            request = ptz_service.create_type('AbsoluteMove')
            request.ProfileToken = profile_token
            request.Position.Zoom._x = zoom
            request.Speed.Zoom._x = speed
            
            ptz_service.AbsoluteMove(request)
            
            logger.info(f"Zoom command sent to camera {camera_id}: zoom={zoom}")
            return True
            
        except Exception as e:
            logger.error(f"Error zooming camera {camera_id}: {str(e)}")
            return False
    
    async def continuous_move(
        self,
        camera_id: int,
        direction: PTZDirection,
        speed: float = 0.5,
        duration: float = 1.0
    ) -> bool:
        """
        Continuous movement in direction
        Useful for button controls
        """
        try:
            if camera_id not in self.ptz_services:
                return False
            
            ptz_service = self.ptz_services[camera_id]['service']
            profile_token = self.ptz_services[camera_id]['profile_token']
            
            # Velocity mapping
            velocity_map = {
                PTZDirection.UP: (0, speed),
                PTZDirection.DOWN: (0, -speed),
                PTZDirection.LEFT: (-speed, 0),
                PTZDirection.RIGHT: (speed, 0),
                PTZDirection.ZOOM_IN: (0, 0, speed),
                PTZDirection.ZOOM_OUT: (0, 0, -speed),
            }
            
            if direction not in velocity_map:
                return False
            
            velocities = velocity_map[direction]
            
            request = ptz_service.create_type('ContinuousMove')
            request.ProfileToken = profile_token
            
            if len(velocities) == 3:  # Zoom
                request.Velocity.Zoom._x = velocities[2]
            else:  # Pan/Tilt
                request.Velocity.PanTilt._x = velocities[0]
                request.Velocity.PanTilt._y = velocities[1]
            
            ptz_service.ContinuousMove(request)
            
            # Stop after duration
            await asyncio.sleep(duration)
            await self.stop_movement(camera_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error continuous move camera {camera_id}: {str(e)}")
            return False
    
    async def stop_movement(self, camera_id: int) -> bool:
        """Stop all PTZ movements"""
        try:
            if camera_id not in self.ptz_services:
                return False
            
            ptz_service = self.ptz_services[camera_id]['service']
            profile_token = self.ptz_services[camera_id]['profile_token']
            
            request = ptz_service.create_type('Stop')
            request.ProfileToken = profile_token
            
            ptz_service.Stop(request)
            return True
            
        except Exception as e:
            logger.error(f"Error stopping camera {camera_id}: {str(e)}")
            return False
    
    async def go_home(self, camera_id: int) -> bool:
        """Return camera to home position"""
        try:
            if camera_id not in self.ptz_services:
                return False
            
            ptz_service = self.ptz_services[camera_id]['service']
            profile_token = self.ptz_services[camera_id]['profile_token']
            
            request = ptz_service.create_type('GotoHomePosition')
            request.ProfileToken = profile_token
            
            ptz_service.GotoHomePosition(request)
            return True
            
        except Exception as e:
            logger.error(f"Error going home for camera {camera_id}: {str(e)}")
            return False
    
    async def save_preset(
        self,
        camera_id: int,
        preset_name: str
    ) -> Optional[str]:
        """Save current camera position as preset"""
        try:
            if camera_id not in self.ptz_services:
                return None
            
            ptz_service = self.ptz_services[camera_id]['service']
            profile_token = self.ptz_services[camera_id]['profile_token']
            
            request = ptz_service.create_type('SetPreset')
            request.ProfileToken = profile_token
            request.PresetName = preset_name
            
            response = ptz_service.SetPreset(request)
            
            logger.info(f"Preset '{preset_name}' saved for camera {camera_id}")
            return response.get('PresetToken')
            
        except Exception as e:
            logger.error(f"Error saving preset for camera {camera_id}: {str(e)}")
            return None
    
    async def goto_preset(
        self,
        camera_id: int,
        preset_token: str
    ) -> bool:
        """Move camera to saved preset"""
        try:
            if camera_id not in self.ptz_services:
                return False
            
            ptz_service = self.ptz_services[camera_id]['service']
            profile_token = self.ptz_services[camera_id]['profile_token']
            
            request = ptz_service.create_type('GotoPreset')
            request.ProfileToken = profile_token
            request.PresetToken = preset_token
            
            ptz_service.GotoPreset(request)
            return True
            
        except Exception as e:
            logger.error(f"Error going to preset for camera {camera_id}: {str(e)}")
            return False


# Singleton instance
_ptz_controller = None

def get_ptz_controller() -> PTZController:
    global _ptz_controller
    if _ptz_controller is None:
        _ptz_controller = PTZController()
    return _ptz_controller