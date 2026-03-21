import io
import asyncio
from PIL import Image, ImageOps
from typing import Optional

# Try to import cv2, but make it optional
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

async def generate_thumbnail(file_data: bytes, max_size: tuple = (200, 200)) -> Optional[bytes]:
    """Generate thumbnail for images and videos"""
    
    # Try to determine if it's an image or video
    try:
        # First try as image
        image = Image.open(io.BytesIO(file_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Generate thumbnail
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        thumb_bytes = io.BytesIO()
        image.save(thumb_bytes, format='JPEG', quality=85)
        thumb_bytes.seek(0)
        
        return thumb_bytes.getvalue()
        
    except Exception as e:
        # If not an image, try as video
        try:
            return await generate_video_thumbnail(file_data, max_size)
        except Exception as e2:
            print(f"Failed to generate thumbnail: {e} (image), {e2} (video)")
            return None

async def generate_video_thumbnail(file_data: bytes, max_size: tuple = (200, 200)) -> Optional[bytes]:
    """Generate thumbnail from video data"""
    
    if not CV2_AVAILABLE:
        print("OpenCV not available, cannot generate video thumbnails")
        return None
        
    try:
        # Save video data to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name
        
        # Open video with OpenCV
        cap = cv2.VideoCapture(temp_path)
        
        if not cap.isOpened():
            os.unlink(temp_path)
            return None
        
        # Read first frame
        ret, frame = cap.read()
        cap.release()
        os.unlink(temp_path)
        
        if not ret:
            return None
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create PIL image
        image = Image.fromarray(frame_rgb)
        
        # Generate thumbnail
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        thumb_bytes = io.BytesIO()
        image.save(thumb_bytes, format='JPEG', quality=85)
        thumb_bytes.seek(0)
        
        return thumb_bytes.getvalue()
        
    except Exception as e:
        print(f"Failed to generate video thumbnail: {e}")
        return None

def get_image_info(file_data: bytes) -> dict:
    """Get image information"""
    try:
        image = Image.open(io.BytesIO(file_data))
        return {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode
        }
    except Exception:
        return {}

def get_video_info(file_data: bytes) -> dict:
    """Get video information"""
    
    if not CV2_AVAILABLE:
        return {}
        
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name
        
        cap = cv2.VideoCapture(temp_path)
        
        if not cap.isOpened():
            os.unlink(temp_path)
            return {}
        
        info = {
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "duration": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
        }
        
        cap.release()
        os.unlink(temp_path)
        
        return info
        
    except Exception as e:
        print(f"Failed to get video info: {e}")
        return {}
