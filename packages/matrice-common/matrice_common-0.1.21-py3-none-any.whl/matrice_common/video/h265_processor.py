"""Clean H.265 encoder/decoder classes for frame-wise and byte-wise streaming."""
import cv2
import subprocess
import threading
import queue
import logging
import time
import numpy as np
from typing import Optional, Generator
import redis

logger = logging.getLogger(__name__)


class H265FrameEncoder:
    """H.265 encoder for individual frames (like your RTSP → Redis frame-wise example)."""
    
    def __init__(self, preset: str = "ultrafast", quality: int = 23, use_hardware: bool = False):
        """Initialize H.265 frame encoder.
        
        Args:
            preset: FFmpeg encoding preset (ultrafast, fast, medium, slow)
            quality: CRF quality (0-51, lower=better quality)
            use_hardware: Use hardware acceleration if available
        """
        self.preset = preset
        self.quality = quality
        self.use_hardware = use_hardware
        
    def encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """Encode single frame to H.265 bytes.
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            H.265 encoded frame bytes or None if failed
        """
        try:
            height, width = frame.shape[:2]
            
            # Build FFmpeg command for single frame H.265 encoding
            cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo",
                "-pix_fmt", "bgr24",
                "-s", f"{width}x{height}",
                "-i", "-",
                "-c:v", "libx265" if not self.use_hardware else "hevc_nvenc",
                "-preset", self.preset,
                "-x265-params", "keyint=1",  # Every frame is keyframe for compatibility
                "-crf", str(self.quality),
                "-f", "hevc",
                "pipe:1"
            ]
            
            # Execute FFmpeg process
            process = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Send frame data and get H.265 output
            stdout, stderr = process.communicate(input=frame.tobytes(), timeout=5)
            
            if process.returncode == 0 and stdout:
                return stdout
            else:
                logger.error(f"Frame encoding failed: {stderr.decode() if stderr else 'Unknown error'}")
                return None
                
        except Exception as e:
            logger.error(f"Frame encoding error: {e}")
            return None


class H265StreamEncoder:
    """H.265 encoder for continuous byte streams (like your RTSP → Redis stream example)."""
    
    def __init__(self, width: int, height: int, fps: int, preset: str = "fast", quality: int = 23, use_hardware: bool = False):
        """Initialize H.265 stream encoder.
        
        Args:
            width: Frame width
            height: Frame height
            fps: Frames per second
            preset: FFmpeg encoding preset
            quality: CRF quality (0-51, lower=better quality)
            use_hardware: Use hardware acceleration if available
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.preset = preset
        self.quality = quality
        self.use_hardware = use_hardware
        self.process: Optional[subprocess.Popen] = None
        
    def start(self) -> bool:
        """Start the continuous H.265 encoding process."""
        if self.process:
            return True
            
        try:
            # Build FFmpeg command for continuous stream encoding
            cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo",
                "-pix_fmt", "bgr24",
                "-s", f"{self.width}x{self.height}",
                "-r", str(self.fps),
                "-i", "-",
                "-c:v", "libx265" if not self.use_hardware else "hevc_nvenc", 
                "-preset", self.preset,
                "-crf", str(self.quality),
                "-f", "hevc",
                "pipe:1"
            ]
            
            # Start FFmpeg process with pipes
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0  # Unbuffered for real-time
            )
            
            logger.info(f"Started H.265 stream encoder: {self.width}x{self.height}@{self.fps}fps")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start H.265 stream encoder: {e}")
            self.stop()
            return False
            
    def stop(self):
        """Stop the encoding process."""
        if self.process:
            try:
                self.process.stdin.close()
                self.process.stdout.close()
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                self.process.kill()
            self.process = None
            
    def encode_frame(self, frame: np.ndarray) -> bool:
        """Add frame to continuous encoding stream.
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            True if frame was added successfully
        """
        if not self.process or not self.process.stdin:
            return False
            
        try:
            self.process.stdin.write(frame.tobytes())
            self.process.stdin.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to encode frame: {e}")
            return False
            
    def read_bytes(self, chunk_size: int = 4096) -> Optional[bytes]:
        """Read encoded H.265 bytes from the stream.
        
        Args:
            chunk_size: Size of chunk to read
            
        Returns:
            H.265 encoded bytes or None
        """
        if not self.process or not self.process.stdout:
            return None
            
        try:
            return self.process.stdout.read(chunk_size)
        except Exception as e:
            logger.error(f"Failed to read H.265 bytes: {e}")
            return None


class H265FrameDecoder:
    """H.265 decoder for individual frames."""
    
    def __init__(self, use_hardware: bool = False):
        """Initialize H.265 frame decoder.
        
        Args:
            use_hardware: Use hardware decoding if available
        """
        self.use_hardware = use_hardware
        
    def decode_frame(self, h265_data: bytes, width: int, height: int) -> Optional[np.ndarray]:
        """Decode H.265 frame to OpenCV frame.
        
        Args:
            h265_data: H.265 encoded frame bytes
            width: Expected frame width
            height: Expected frame height
            
        Returns:
            OpenCV frame (BGR format) or None if failed
        """
        try:
            # Build FFmpeg command for single frame decoding
            cmd = [
                "ffmpeg", "-y",
                "-f", "hevc",
                "-i", "-",
                "-f", "rawvideo", 
                "-pix_fmt", "bgr24",
                "pipe:1"
            ]
            
            # Execute FFmpeg
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Send H.265 data and get raw frame
            stdout, stderr = process.communicate(input=h265_data, timeout=5)
            
            if process.returncode == 0 and stdout:
                # Convert raw bytes to OpenCV frame
                frame_data = np.frombuffer(stdout, dtype=np.uint8)
                
                # Calculate expected frame size
                expected_size = width * height * 3  # BGR
                if len(frame_data) >= expected_size:
                    frame = frame_data[:expected_size].reshape((height, width, 3))
                    return frame
                else:
                    logger.error(f"Insufficient frame data: {len(frame_data)}/{expected_size}")
                    return None
            else:
                logger.error(f"Frame decoding failed: {stderr.decode() if stderr else 'Unknown error'}")
                return None
                
        except Exception as e:
            logger.error(f"Frame decoding error: {e}")
            return None


class H265StreamDecoder:
    """H.265 decoder for continuous byte streams."""
    
    def __init__(self, width: int, height: int, use_hardware: bool = False):
        """Initialize H.265 stream decoder.
        
        Args:
            width: Expected frame width
            height: Expected frame height
            use_hardware: Use hardware decoding if available
        """
        self.width = width
        self.height = height
        self.use_hardware = use_hardware
        self.process: Optional[subprocess.Popen] = None
        
    def start(self) -> bool:
        """Start the continuous H.265 decoding process."""
        if self.process:
            return True
            
        try:
            # Build FFmpeg command for continuous stream decoding
            cmd = [
                "ffmpeg", "-y",
                "-f", "hevc",
                "-i", "-",
                "-f", "rawvideo",
                "-pix_fmt", "bgr24",
                "pipe:1"
            ]
            
            # Start FFmpeg process
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0  # Unbuffered for real-time
            )
            
            logger.info(f"Started H.265 stream decoder: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start H.265 stream decoder: {e}")
            self.stop()
            return False
            
    def stop(self):
        """Stop the decoding process."""
        if self.process:
            try:
                self.process.stdin.close()
                self.process.stdout.close()
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                self.process.kill()
            self.process = None
            
    def decode_bytes(self, h265_chunk: bytes) -> bool:
        """Add H.265 bytes to decoding stream.
        
        Args:
            h265_chunk: H.265 encoded bytes
            
        Returns:
            True if bytes were added successfully
        """
        if not self.process or not self.process.stdin:
            return False
            
        try:
            self.process.stdin.write(h265_chunk)
            self.process.stdin.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to decode bytes: {e}")
            return False
            
    def read_frame(self) -> Optional[np.ndarray]:
        """Read next decoded frame from stream.
        
        Returns:
            OpenCV frame (BGR format) or None
        """
        if not self.process or not self.process.stdout:
            return None
            
        try:
            # Read one complete frame
            frame_size = self.width * self.height * 3  # BGR
            frame_data = self.process.stdout.read(frame_size)
            
            if len(frame_data) == frame_size:
                frame = np.frombuffer(frame_data, dtype=np.uint8)
                frame = frame.reshape((self.height, self.width, 3))
                return frame
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to read decoded frame: {e}")
            return None


# Consumer Classes for Redis Integration

class H265FrameConsumer:
    """Consumer for frame-wise H.265 from Redis (like your consumer example)."""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """Initialize frame consumer."""
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.decoder = H265FrameDecoder()
        
    def consume_frames(self, channel: str, width: int, height: int) -> Generator[np.ndarray, None, None]:
        """Consume H.265 frames from Redis channel.
        
        Args:
            channel: Redis channel name
            width: Frame width
            height: Frame height
            
        Yields:
            Decoded OpenCV frames
        """
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(channel)
        
        logger.info(f"Consuming H.265 frames from channel: {channel}")
        
        try:
            for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                    
                try:
                    h265_data = message["data"]
                    frame = self.decoder.decode_frame(h265_data, width, height)
                    if frame is not None:
                        yield frame
                except Exception as e:
                    logger.error(f"Frame decode error: {e}")
                    
        finally:
            pubsub.close()


class H265StreamConsumer:
    """Consumer for continuous H.265 stream from Redis (like your stream consumer example)."""
    
    def __init__(self, width: int, height: int, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """Initialize stream consumer."""
        self.width = width
        self.height = height
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.decoder = H265StreamDecoder(width, height)
        self.frame_queue = queue.Queue(maxsize=30)
        self.stop_consuming = False
        
    def start_consuming(self, channel: str) -> bool:
        """Start consuming H.265 stream from Redis.
        
        Args:
            channel: Redis channel name
            
        Returns:
            True if started successfully
        """
        if not self.decoder.start():
            return False
            
        # Start Redis consumer thread
        self.stop_consuming = False
        self.redis_thread = threading.Thread(target=self._consume_redis_stream, args=(channel,), daemon=True)
        self.frame_reader_thread = threading.Thread(target=self._read_frames, daemon=True)
        
        self.redis_thread.start()
        self.frame_reader_thread.start()
        
        logger.info(f"Started consuming H.265 stream from channel: {channel}")
        return True
        
    def stop_consuming(self):
        """Stop consuming."""
        self.stop_consuming = True
        self.decoder.stop()
        
    def get_frames(self) -> Generator[np.ndarray, None, None]:
        """Generator that yields decoded frames."""
        while not self.stop_consuming:
            try:
                frame = self.frame_queue.get(timeout=0.1)
                yield frame
            except queue.Empty:
                continue
                
    def _consume_redis_stream(self, channel: str):
        """Background thread to consume H.265 chunks from Redis."""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(channel)
        
        try:
            for message in pubsub.listen():
                if self.stop_consuming:
                    break
                    
                if message["type"] != "message":
                    continue
                    
                try:
                    h265_chunk = message["data"]
                    self.decoder.decode_bytes(h265_chunk)
                except Exception as e:
                    logger.error(f"Stream decode error: {e}")
        finally:
            pubsub.close()
            
    def _read_frames(self):
        """Background thread to read decoded frames."""
        while not self.stop_consuming:
            try:
                frame = self.decoder.read_frame()
                if frame is not None:
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame)
                    else:
                        # Drop oldest frame
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put(frame)
                        except queue.Empty:
                            pass
                else:
                    time.sleep(0.001)  # Small delay if no frame
            except Exception as e:
                logger.error(f"Frame read error: {e}")


# Utility functions for easy usage
def encode_frame_h265(frame: np.ndarray, quality: int = 23) -> Optional[bytes]:
    """Quick utility to encode a frame to H.265."""
    encoder = H265FrameEncoder(quality=quality)
    return encoder.encode_frame(frame)


def decode_frame_h265(h265_data: bytes, width: int, height: int) -> Optional[np.ndarray]:
    """Quick utility to decode H.265 frame.""" 
    decoder = H265FrameDecoder()
    return decoder.decode_frame(h265_data, width, height)