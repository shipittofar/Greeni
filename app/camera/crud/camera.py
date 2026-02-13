from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from app.camera.models.camera import Camera, PTZControl, CameraStatus
from app.camera.schemas.camera import CameraCreate, CameraUpdate

class CRUDCamera:
    """CRUD operations for Camera model"""
    
    def __init__(self, model: type):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[Camera]:
        """Get camera by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Camera]:
        """Get all cameras"""
        return db.query(self.model).offset(skip).limit(limit).all()

    # def get_all_cameras(self, db: Session) -> List[Camera]:
    #     """Get all cameras"""
    #     return db.query(self.model).all()

    def get_non_pending(self, db: Session, only_active: bool = False, skip: int = 0, limit: int = 100) -> List[Camera]:
        query = db.query(self.model).filter(self.model.is_pending == False)
        if only_active:
            query = query.filter(self.model.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    def get_by_device(self, db: Session, device_id: int) -> List[Camera]:
        """Get all cameras for a device"""
        return db.query(self.model).filter(self.model.device_id == device_id).all()
    
    def get_pending_cameras(self, db: Session) -> List[Camera]:
        """Get all cameras that are pending and not active"""
        return (
            db.query(Camera)
            .filter(Camera.is_pending == True)
            .all()
        )

    def get_active(self, db: Session, device_id: int) -> List[Camera]:
        """Get active cameras for a device"""
        return db.query(self.model).filter(
            and_(
                self.model.device_id == device_id,
                self.model.is_active == True
            )
        ).all()
    
    def get_all_active(self, db: Session):
        return db.query(Camera).filter(Camera.is_pending == False).all()

    def get_with_ptz(self, db: Session, device_id: int) -> List[Camera]:
        """Get cameras with PTZ support"""
        return db.query(self.model).filter(
            and_(
                self.model.device_id == device_id,
                self.model.has_ptz == True
            )
        ).all()
    
    def create(self, db: Session, obj_in: CameraCreate) -> Camera:
        """Create new camera (starts in pending state)"""
        db_obj = self.model(
            device_id=obj_in.device_id,
            name=obj_in.name,
            type=obj_in.type,
            url=obj_in.url,
            username=obj_in.username,
            password=obj_in.password,
            port=obj_in.port,
            resolution_width=obj_in.resolution_width,
            resolution_height=obj_in.resolution_height,
            fps=obj_in.fps,
            has_ptz=obj_in.has_ptz,
            ptz_type=obj_in.ptz_type,
            streaming_enabled=obj_in.streaming_enabled,
            streaming_bitrate=obj_in.streaming_bitrate,
            streaming_quality=obj_in.streaming_quality,
            recording_enabled=obj_in.recording_enabled,
            retention_days=obj_in.retention_days,
            location=obj_in.location,
            is_pending=True,  # Always start in pending state
            is_active=False,  # Start as inactive until approved
            status=CameraStatus.OFFLINE,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: Camera, obj_in: CameraUpdate) -> Camera:
        """Update camera"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_status(
        self,
        db: Session,
        camera_id: int,
        status: str
    ) -> Optional[Camera]:
        """Update camera status (online/offline/error)"""
        camera = db.query(self.model).filter(self.model.id == camera_id).first()
        if camera:
            camera.status = status
            camera.last_heartbeat = datetime.utcnow()
            db.add(camera)
            db.commit()
            db.refresh(camera)
        return camera
    
    def activate_camera(self, db: Session, camera_id: int) -> Optional[Camera]:
        """Activate a pending camera or manually activate any camera"""
        camera = db.query(self.model).filter(self.model.id == camera_id).first()
        if camera:
            camera.is_pending = False
            camera.is_active = True
            camera.status = CameraStatus.ONLINE
            camera.updated_at = datetime.utcnow()
            db.add(camera)
            db.commit()
            db.refresh(camera)
        return camera
    
    def deactivate_camera(self, db: Session, camera_id: int) -> Optional[Camera]:
        """Deactivate a camera"""
        camera = db.query(self.model).filter(self.model.id == camera_id).first()
        if camera:
            camera.is_active = False
            camera.status = CameraStatus.OFFLINE
            camera.updated_at = datetime.utcnow()
            db.add(camera)
            db.commit()
            db.refresh(camera)
        return camera
    
    def reject_pending_camera(self, db: Session, camera_id: int) -> bool:
        """Reject and delete a pending camera"""
        camera = db.query(self.model).filter(
            and_(
                self.model.id == camera_id,
                self.model.is_pending == True
            )
        ).first()
        if camera:
            db.delete(camera)
            db.commit()
            return True
        return False
    
    def get_pending_count(self, db: Session) -> int:
        """Get count of pending cameras"""
        return db.query(self.model).filter(self.model.is_pending == True).count()
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete camera"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
    
    def remove(self, db: Session, id: int) -> bool:
        """Alias for delete"""
        return self.delete(db, id)


class CRUDPTZControl:
    """CRUD operations for PTZ Control"""
    
    def __init__(self, model: type):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[PTZControl]:
        """Get PTZ control by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_camera(self, db: Session, camera_id: int) -> Optional[PTZControl]:
        """Get PTZ control for camera"""
        return db.query(self.model).filter(self.model.camera_id == camera_id).first()
    
    def create_or_update(
        self,
        db: Session,
        camera_id: int,
        ptz_data: dict
    ) -> PTZControl:
        """Create or update PTZ control"""
        ptz = db.query(self.model).filter(self.model.camera_id == camera_id).first()
        
        if ptz:
            for key, value in ptz_data.items():
                if hasattr(ptz, key):
                    setattr(ptz, key, value)
        else:
            ptz_data['camera_id'] = camera_id
            ptz = self.model(**ptz_data)
        
        ptz.updated_at = datetime.utcnow()
        db.add(ptz)
        db.commit()
        db.refresh(ptz)
        return ptz
    
    def get_preset(
        self,
        db: Session,
        camera_id: int,
        preset_name: str
    ) -> Optional[PTZControl]:
        """Get saved preset for camera"""
        return db.query(self.model).filter(
            and_(
                self.model.camera_id == camera_id,
                self.model.preset_name == preset_name
            )
        ).first()
    
    def get_presets(self, db: Session, camera_id: int) -> List[PTZControl]:
        """Get all presets for camera"""
        return db.query(self.model).filter(
            and_(
                self.model.camera_id == camera_id,
                self.model.preset_name.isnot(None)
            )
        ).all()
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete PTZ control"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False


# Instances
camera_crud = CRUDCamera(Camera)
ptz_crud = CRUDPTZControl(PTZControl)