"""
Local file storage with multi-level folder support
Provides persistent storage on disk instead of just in-memory
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import hashlib
from datetime import datetime


@dataclass
class FileMetadata:
    """Metadata for stored files"""
    path: str
    size: int
    created_at: str
    modified_at: str
    checksum: str
    content_type: str = "text/plain"


class LocalFileStorage:
    """
    Local file storage manager with multi-level folder support.
    
    Features:
    - Multi-level directory structure
    - File metadata tracking
    - Safe file operations with validation
    - Search and filtering capabilities
    """
    
    def __init__(self, base_path: str = "./agent_workspace"):
        """
        Initialize local file storage.
        
        Args:
            base_path: Root directory for all file operations
        """
        self.base_path = Path(base_path).resolve()
        self.metadata_file = self.base_path / ".metadata.json"
        self._ensure_base_directory()
        self._load_metadata()
    
    def _ensure_base_directory(self):
        """Create base directory if it doesn't exist"""
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _load_metadata(self):
        """Load file metadata from disk"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metadata = {k: FileMetadata(**v) for k, v in data.items()}
        else:
            self.metadata: Dict[str, FileMetadata] = {}
            # Create empty metadata file on initialization
            self._save_metadata()
    
    def _save_metadata(self):
        """Save file metadata to disk"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            data = {k: asdict(v) for k, v in self.metadata.items()}
            json.dump(data, f, indent=2)
    
    def _normalize_path(self, path: str) -> Path:
        """Normalize and validate path"""
        # Remove leading/trailing slashes and normalize
        path = path.strip('/\\')
        full_path = (self.base_path / path).resolve()
        
        # Security check: ensure path is within base_path
        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError(f"Invalid path: {path} (outside workspace)")
        
        return full_path
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate MD5 checksum of content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def write_file(self, path: str, content: str, content_type: str = "text/plain") -> FileMetadata:
        """
        Write content to a file (supports nested directories).
        
        Args:
            path: Relative path to file (e.g., "data/sales/2024.csv")
            content: Content to write
            content_type: MIME type of content
            
        Returns:
            FileMetadata object
            
        Example:
            storage.write_file("reports/q1/summary.txt", "Q1 Summary...")
        """
        full_path = self._normalize_path(path)
        
        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update metadata
        now = datetime.now().isoformat()
        metadata = FileMetadata(
            path=path,
            size=len(content.encode('utf-8')),
            created_at=self.metadata.get(path).created_at if path in self.metadata else now,
            modified_at=now,
            checksum=self._calculate_checksum(content),
            content_type=content_type
        )
        
        self.metadata[path] = metadata
        self._save_metadata()
        
        return metadata
    
    def read_file(self, path: str) -> str:
        """
        Read content from a file.
        
        Args:
            path: Relative path to file
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        full_path = self._normalize_path(path)
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: Relative path to file
            
        Returns:
            True if deleted successfully
        """
        full_path = self._normalize_path(path)
        
        if full_path.exists() and full_path.is_file():
            full_path.unlink()
            if path in self.metadata:
                del self.metadata[path]
                self._save_metadata()
            return True
        
        return False
    
    def list_files(self, directory: str = "", recursive: bool = True) -> List[str]:
        """
        List files in a directory.
        
        Args:
            directory: Directory path (empty string for root)
            recursive: Whether to list files recursively
            
        Returns:
            List of relative file paths
            
        Example:
            # List all files recursively
            files = storage.list_files()
            
            # List only files in 'data' directory
            files = storage.list_files("data", recursive=False)
        """
        if directory:
            full_path = self._normalize_path(directory)
        else:
            full_path = self.base_path
        
        if not full_path.exists():
            return []
        
        files = []
        pattern = "**/*" if recursive else "*"
        
        for item in full_path.glob(pattern):
            if item.is_file() and item.name != ".metadata.json":
                rel_path = item.relative_to(self.base_path)
                files.append(str(rel_path).replace('\\', '/'))
        
        return sorted(files)
    
    def list_directories(self, directory: str = "", recursive: bool = True) -> List[str]:
        """
        List directories.
        
        Args:
            directory: Starting directory (empty for root)
            recursive: Whether to list recursively
            
        Returns:
            List of relative directory paths
        """
        if directory:
            full_path = self._normalize_path(directory)
        else:
            full_path = self.base_path
        
        if not full_path.exists():
            return []
        
        directories = []
        pattern = "**/*" if recursive else "*"
        
        for item in full_path.glob(pattern):
            if item.is_dir():
                rel_path = item.relative_to(self.base_path)
                directories.append(str(rel_path).replace('\\', '/'))
        
        return sorted(directories)
    
    def create_directory(self, path: str) -> Path:
        """
        Create a directory (including parent directories).
        
        Args:
            path: Directory path to create
            
        Returns:
            Full Path object
        """
        full_path = self._normalize_path(path)
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path
    
    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """
        Delete a directory.
        
        Args:
            path: Directory path
            recursive: Whether to delete non-empty directories
            
        Returns:
            True if deleted successfully
        """
        full_path = self._normalize_path(path)
        
        if not full_path.exists() or not full_path.is_dir():
            return False
        
        try:
            if recursive:
                shutil.rmtree(full_path)
                # Remove metadata for all files in this directory
                prefix = path + "/"
                keys_to_remove = [k for k in self.metadata.keys() if k.startswith(prefix)]
                for key in keys_to_remove:
                    del self.metadata[key]
                self._save_metadata()
            else:
                full_path.rmdir()  # Only works if empty
            return True
        except Exception:
            return False
    
    def get_metadata(self, path: str) -> Optional[FileMetadata]:
        """
        Get metadata for a file.
        
        Args:
            path: File path
            
        Returns:
            FileMetadata object or None if not found
        """
        return self.metadata.get(path)
    
    def search_files(self, pattern: str, directory: str = "") -> List[str]:
        """
        Search for files matching a pattern.
        
        Args:
            pattern: Glob pattern (e.g., "*.csv", "**/*.json")
            directory: Directory to search in
            
        Returns:
            List of matching file paths
            
        Example:
            # Find all CSV files
            csv_files = storage.search_files("*.csv")
            
            # Find JSON files in reports directory
            json_files = storage.search_files("*.json", "reports")
        """
        if directory:
            search_path = self._normalize_path(directory)
        else:
            search_path = self.base_path
        
        if not search_path.exists():
            return []
        
        # If pattern doesn't start with **, make it recursive by default
        if not pattern.startswith("**/"):
            pattern = f"**/{pattern}"
        
        files = []
        for item in search_path.glob(pattern):
            if item.is_file() and item.name != ".metadata.json":
                rel_path = item.relative_to(self.base_path)
                files.append(str(rel_path).replace('\\', '/'))
        
        return sorted(files)
    
    def get_tree(self, directory: str = "", max_depth: int = None) -> Dict[str, Any]:
        """
        Get directory tree structure.
        
        Args:
            directory: Starting directory
            max_depth: Maximum depth to traverse (None for unlimited)
            
        Returns:
            Nested dictionary representing the directory structure
            
        Example:
            tree = storage.get_tree()
            # {'data': {'sales': ['2024.csv', '2023.csv'], 'reports': [...]}, ...}
        """
        if directory:
            start_path = self._normalize_path(directory)
        else:
            start_path = self.base_path
        
        def build_tree(path: Path, depth: int = 0) -> Dict[str, Any]:
            if max_depth is not None and depth >= max_depth:
                return {}
            
            tree = {}
            
            try:
                for item in sorted(path.iterdir()):
                    if item.name == ".metadata.json":
                        continue
                    
                    rel_name = item.name
                    
                    if item.is_dir():
                        tree[rel_name] = build_tree(item, depth + 1)
                    else:
                        if "_files" not in tree:
                            tree["_files"] = []
                        tree["_files"].append(rel_name)
            except PermissionError:
                pass
            
            return tree
        
        return build_tree(start_path)
    
    def copy_file(self, src_path: str, dst_path: str) -> FileMetadata:
        """
        Copy a file to a new location.
        
        Args:
            src_path: Source file path
            dst_path: Destination file path
            
        Returns:
            FileMetadata for the new file
        """
        content = self.read_file(src_path)
        metadata = self.get_metadata(src_path)
        content_type = metadata.content_type if metadata else "text/plain"
        
        return self.write_file(dst_path, content, content_type)
    
    def move_file(self, src_path: str, dst_path: str) -> FileMetadata:
        """
        Move a file to a new location.
        
        Args:
            src_path: Source file path
            dst_path: Destination file path
            
        Returns:
            FileMetadata for the moved file
        """
        new_metadata = self.copy_file(src_path, dst_path)
        self.delete_file(src_path)
        return new_metadata
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about the storage.
        
        Returns:
            Dictionary with storage statistics
        """
        total_files = len(self.metadata)
        total_size = sum(m.size for m in self.metadata.values())
        
        return {
            "base_path": str(self.base_path),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "directories": len(self.list_directories())
        }
