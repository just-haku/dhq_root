import os
import uuid
import subprocess
from PIL import Image, ImageOps
from io import BytesIO
import mimetypes

from app.core.storage import storage_service

# Thumbnail settings
THUMBNAIL_SIZE = (150, 150)
SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
SUPPORTED_VIDEO_TYPES = ['video/mp4', 'video/avi', 'video/mkv', 'video/webm', 'video/quicktime', 'video/x-msvideo']

def ensure_thumbnail_dir(storage_path):
    """Ensure thumbnail directory exists"""
    thumbnail_dir = os.path.join(storage_path, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)
    return thumbnail_dir

def generate_thumbnail(file_path, file_id):
    """Generate thumbnail for an image, video, or PDF file"""
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # For images, natively return the original file to act as its own thumbnail
        if mime_type in SUPPORTED_IMAGE_TYPES:
            return file_path
            
        # For videos, leverage FFmpeg to extract the first frame
        elif mime_type and mime_type.startswith('video/'):
            storage_path = storage_service.get_available_storage_path()
            thumbnail_dir = ensure_thumbnail_dir(storage_path)
            thumbnail_filename = f"{file_id}_thumb.jpg"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            
            try:
                subprocess.run([
                    'ffmpeg', '-hwaccel', 'none', '-threads', '1', '-y', '-i', file_path, '-vframes', '1', thumbnail_path
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(thumbnail_path):
                    return thumbnail_path
            except Exception as e:
                print(f"Error extracting video frame for {file_path}: {e}")

        # For PDFs, use PyMuPDF to render the first page
        elif mime_type == 'application/pdf' or file_path.lower().endswith('.pdf'):
            try:
                import fitz  # PyMuPDF
                storage_path = storage_service.get_available_storage_path()
                thumbnail_dir = ensure_thumbnail_dir(storage_path)
                thumbnail_filename = f"{file_id}_thumb.jpg"
                thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

                doc = fitz.open(file_path)
                if doc.page_count > 0:
                    page = doc.load_page(0)
                    # Render at 2x resolution for clarity
                    mat = fitz.Matrix(2.0, 2.0)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("jpeg")
                    
                    # Resize to thumbnail size with PIL
                    img = Image.open(BytesIO(img_data))
                    img.thumbnail((300, 400), Image.LANCZOS)
                    img.save(thumbnail_path, "JPEG", quality=85)
                    doc.close()
                    return thumbnail_path
                doc.close()
            except Exception as e:
                print(f"Error generating PDF thumbnail for {file_path}: {e}")
                
        return None
            
    except Exception as e:
        print(f"Error generating thumbnail for {file_path}: {e}")
        return None

def get_thumbnail_path(file_id, encrypted=False):
    """Get thumbnail path for a file"""
    thumbnail_filename = f"{file_id}_thumb.jpg"
    if encrypted:
        thumbnail_filename += ".enc"
    
    for storage_path in storage_service.get_all_storage_paths():
        thumbnail_path = os.path.join(storage_path, "thumbnails", thumbnail_filename)
        if os.path.exists(thumbnail_path):
            return thumbnail_path
    
    return None

def delete_thumbnail(file_id, encrypted=False):
    """Delete thumbnail for a file"""
    thumbnail_filename = f"{file_id}_thumb.jpg"
    if encrypted:
        thumbnail_filename += ".enc"
    
    for storage_path in storage_service.get_all_storage_paths():
        thumbnail_path = os.path.join(storage_path, "thumbnails", thumbnail_filename)
        try:
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        except Exception as e:
            print(f"Error deleting thumbnail {thumbnail_path}: {e}")

def get_file_icon(filename):
    """Get appropriate icon for file type"""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    
    icon_map = {
        # Documents
        'pdf': '📄',
        'doc': '📝', 'docx': '📝',
        'xls': '📊', 'xlsx': '📊',
        'ppt': '📈', 'pptx': '📈',
        'txt': '📄', 'rtf': '📄',
        'odt': '📄', 'ods': '📊', 'odp': '📈',
        
        # Images
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
        'bmp': '🖼️', 'webp': '🖼️', 'svg': '🖼️', 'ico': '🖼️',
        
        # Videos
        'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'wmv': '🎬',
        'flv': '🎬', 'mkv': '🎬', 'webm': '🎬', 'm4v': '🎬',
        
        # Audio
        'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵',
        'ogg': '🎵', 'wma': '🎵', 'm4a': '🎵',
        
        # Archives
        'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦',
        'gz': '📦', 'bz2': '📦', 'xz': '📦',
        
        # Code
        'js': '📜', 'html': '🌐', 'css': '🎨', 'py': '🐍',
        'java': '☕', 'cpp': '⚙️', 'c': '⚙️', 'php': '🐘',
        'rb': '💎', 'go': '🐹', 'rs': '🦀', 'swift': '🍎',
        'kt': '🎯', 'scala': '🔷', 'sql': '🗃️', 'xml': '📄',
        'json': '📋', 'yaml': '📋', 'yml': '📋', 'md': '📝',
        
        # Other
        'exe': '⚙️', 'msi': '⚙️', 'deb': '📦', 'rpm': '📦',
        'dmg': '💿', 'iso': '💿', 'img': '💿'
    }
    
    return icon_map.get(ext, '📄')
