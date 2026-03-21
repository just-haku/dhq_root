import os
import shutil
from typing import List
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.storages = []
        # Attempt to load dynamically configured storages
        for i in range(1, getattr(settings, 'NUMBER_OF_STORAGES', 1) + 1):
            path = getattr(settings, f'STORAGE{i}', None)
            # Accept valid paths. Exclude placeholders like '#'
            if path and path.strip() != '#' and path.strip() != '':
                self.storages.append(path.strip())
        
        # Fallback if no valid storages are configured
        if not self.storages:
            self.storages = ["/home/haku/storage"]
            
        # Ensure at least the primary configuration is made, even if it doesn't exist yet
        # For missing directories, we'll try to create it if we need to write to it.
        # It's better not to create hdd mounts if they aren't mounted though!
        
        # We require at least 5GB free before we consider a drive "almost full"
        self.MIN_FREE_SPACE = 5 * 1024 * 1024 * 1024

    def get_available_storage_path(self, required_size: int = 0) -> str:
        """Finds the first mounted storage drive with enough free space."""
        for storage in self.storages:
            # We enforce that the storage path exists. If it's a mount point like hdd2,
            # it should be mounted and the directory should be accessible.
            if not os.path.exists(storage):
                # Try to create it if it's just a local directory, but for 
                # extra drives (hdd2), we'd prefer them to be mounted by the OS.
                # Let's try to create it. If it fails (permissions), we skip.
                try:
                    os.makedirs(storage, exist_ok=True)
                except Exception:
                    continue
            
            try:
                free_space = shutil.disk_usage(storage).free
                if free_space > (required_size + self.MIN_FREE_SPACE):
                    return storage
            except Exception as e:
                print(f"Failed getting disk usage for {storage}: {e}")
                continue
        
        # If all valid storages are full or failing, fallback to the primary one
        # and hope for the best.
        if self.storages:
            return self.storages[0]
        
        return "/home/haku/storage"

    def get_all_storage_paths(self) -> List[str]:
        """Returns all configured storage paths (useful for sweeping files)."""
        return self.storages

storage_service = StorageService()
