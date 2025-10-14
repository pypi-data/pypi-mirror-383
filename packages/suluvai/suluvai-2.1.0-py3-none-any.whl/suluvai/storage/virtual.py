"""
Virtual filesystem storage (in-memory, state-based)
DeepAgents compatible
"""

from typing import Dict, List, Any
import fnmatch


class VirtualStorage:
    """
    Virtual filesystem that operates on agent state.
    Files are stored in state["files"] dictionary.
    """
    
    def __init__(self):
        self.files: Dict[str, str] = {}
    
    def write_file(self, filepath: str, content: str) -> bool:
        """Write file to virtual filesystem"""
        self.files[filepath] = content
        return True
    
    def read_file(self, filepath: str) -> str:
        """Read file from virtual filesystem"""
        if filepath not in self.files:
            raise FileNotFoundError(f"File not found: {filepath}")
        return self.files[filepath]
    
    def list_files(self, directory: str = "", recursive: bool = True) -> List[str]:
        """List files in directory"""
        if not directory:
            return list(self.files.keys())
        
        result = []
        for filepath in self.files.keys():
            if filepath.startswith(directory):
                if recursive or '/' not in filepath[len(directory):].lstrip('/'):
                    result.append(filepath)
        return result
    
    def delete_file(self, filepath: str) -> bool:
        """Delete file"""
        if filepath in self.files:
            del self.files[filepath]
            return True
        return False
    
    def search_files(self, pattern: str, directory: str = "") -> List[str]:
        """Search files by glob pattern"""
        files = self.list_files(directory, recursive=True)
        return [f for f in files if fnmatch.fnmatch(f, pattern)]
    
    def get_tree(self, directory: str = "", max_depth: int = 3) -> Dict:
        """Get directory tree structure"""
        tree = {}
        files = self.list_files(directory, recursive=True)
        
        for filepath in files:
            parts = filepath.split('/')
            current = tree
            for i, part in enumerate(parts[:-1]):
                if i >= max_depth:
                    break
                if part not in current:
                    current[part] = {}
                current = current[part]
            if "_files" not in current:
                current["_files"] = []
            current["_files"].append(parts[-1])
        
        return tree
    
    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """Copy file"""
        content = self.read_file(src_path)
        self.write_file(dst_path, content)
        return True
    
    def move_file(self, src_path: str, dst_path: str) -> bool:
        """Move file"""
        self.copy_file(src_path, dst_path)
        self.delete_file(src_path)
        return True
