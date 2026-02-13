import asyncio
import cv2
import logging
from typing import Optional, AsyncGenerator
import subprocess
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class StreamingManager:
    """Handle camera streaming in different formats"""
    
    def __init__(self):
        self.streams = {}
        self.processes = {}
    
    async def start_mjpeg_stream(
        self,
        camera_id: int,
        cap,
        quality: int = 80
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream camera as Motion JPEG (MJPEG)
        Suitable for real-time browser streaming
        """
        try:
            while camera_id in self.streams and self.streams[camera_id].get('active'):
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame from camera {camera_id}")
                    break
                
                # Encode frame as JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                if not ret:
                    continue
                
                # MJPEG boundary format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(buffer)).encode() + b'\r\n\r\n'
                       + buffer + b'\r\n')
                
                # Control frame rate
                await asyncio.sleep(1 / 30)  # 30 FPS
                
        except Exception as e:
            logger.error(f"Error in MJPEG stream for camera {camera_id}: {str(e)}")
        finally:
            if camera_id in self.streams:
                self.streams[camera_id]['active'] = False
    
    async def start_hls_stream(
        self,
        camera_id: int,
        rtsp_url: str,
        output_dir: str = "/tmp/streams",
        segment_duration: int = 2
    ) -> str:
        """
        Start HLS stream using FFmpeg
        Returns path to m3u8 playlist
        """
        try:
            # Create output directory
            output_path = Path(output_dir) / f"camera_{camera_id}"
            output_path.mkdir(parents=True, exist_ok=True)
            
            playlist_path = output_path / "playlist.m3u8"
            segment_pattern = str(output_path / "segment_%03d.ts")
            
            # FFmpeg command for HLS
            cmd = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',
                '-i', rtsp_url,
                '-c:v', 'libx264',
                '-preset', 'veryfast',
                '-b:v', '2500k',
                '-maxrate', '2500k',
                '-bufsize', '5000k',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-f', 'hls',
                '-hls_time', str(segment_duration),
                '-hls_list_size', '10',
                '-hls_flags', 'delete_segments',
                str(playlist_path)
            ]
            
            # Start FFmpeg process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.processes[camera_id] = process
            self.streams[camera_id] = {
                'type': 'hls',
                'playlist': str(playlist_path),
                'process': process,
                'active': True
            }
            
            logger.info(f"Started HLS stream for camera {camera_id}: {playlist_path}")
            return str(playlist_path)
            
        except Exception as e:
            logger.error(f"Error starting HLS stream for camera {camera_id}: {str(e)}")
            return None
    
    async def stop_stream(self, camera_id: int) -> bool:
        """Stop streaming for camera"""
        try:
            if camera_id in self.streams:
                self.streams[camera_id]['active'] = False
            
            if camera_id in self.processes:
                process = self.processes[camera_id]
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                
                del self.processes[camera_id]
            
            if camera_id in self.streams:
                del self.streams[camera_id]
            
            logger.info(f"Stopped stream for camera {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping stream for camera {camera_id}: {str(e)}")
            return False
    
    async def get_stream_status(self, camera_id: int) -> Optional[dict]:
        """Get current stream status"""
        if camera_id in self.streams:
            stream = self.streams[camera_id]
            return {
                'camera_id': camera_id,
                'type': stream.get('type'),
                'active': stream.get('active'),
                'playlist': stream.get('playlist')
            }
        return None


# Singleton instance
_streaming_manager = None

def get_streaming_manager() -> StreamingManager:
    global _streaming_manager
    if _streaming_manager is None:
        _streaming_manager = StreamingManager()
    return _streaming_manager