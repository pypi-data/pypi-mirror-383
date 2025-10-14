"""
Hybrid storage combining virtual and local filesystems
"""

from typing import List, Dict
from suluvai.storage.virtual import VirtualStorage
from suluvai.storage.local_storage import LocalFileStorage


class HybridStorage:
    """
    Hybrid storage that combines virtual and local filesystems.
    
    - Files are stored in virtual by default
    - Files prefixed with 'output/' or marked persistent go to local
    - Provides unified interface to both
    """
    
    def __init__(self, local_path: str):
        self.virtual = VirtualStorage()
        self.local = LocalFileStorage(local_path)
        self.persistent_prefixes = ['output/', 'final/', 'results/']
    
    def _is_persistent(self, filepath: str) -> bool:
        """Check if file should be stored locally"""
        return any(filepath.startswith(prefix) for prefix in self.persistent_prefixes)
    
    def write_file(self, filepath: str, content: str):
        """Write to appropriate storage"""
        if self._is_persistent(filepath):
            return self.local.write_file(filepath, content)
        else:
            return self.virtual.write_file(filepath, content)
    
    def read_file(self, filepath: str) -> str:
        """Read from appropriate storage"""
        if self._is_persistent(filepath):
            return self.local.read_file(filepath)
        else:
            return self.virtual.read_file(filepath)
    
    def list_files(self, directory: str = "", recursive: bool = True) -> List[str]:
        """List files from both storages"""
        virtual_files = self.virtual.list_files(directory, recursive)
        local_files = self.local.list_files(directory, recursive)
        return sorted(set(virtual_files + local_files))
    
    def delete_file(self, filepath: str) -> bool:
        """Delete from appropriate storage"""
        if self._is_persistent(filepath):
            return self.local.delete_file(filepath)
        else:
            return self.virtual.delete_file(filepath)
    
    def search_files(self, pattern: str, directory: str = "") -> List[str]:
        """Search in both storages"""
        virtual_results = self.virtual.search_files(pattern, directory)
        local_results = self.local.search_files(pattern, directory)
        return sorted(set(virtual_results + local_results))
    
    def get_tree(self, directory: str = "", max_depth: int = 3) -> Dict:
        """Get combined tree"""
        # For now, return local tree (most persistent data)
        return self.local.get_tree(directory, max_depth)
    
    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """Copy file (can cross storage boundaries)"""
        content = self.read_file(src_path)
        self.write_file(dst_path, content)
        return True
    
    def move_file(self, src_path: str, dst_path: str) -> bool:
        """Move file (can cross storage boundaries)"""
        self.copy_file(src_path, dst_path)
        self.delete_file(src_path)
        return True
