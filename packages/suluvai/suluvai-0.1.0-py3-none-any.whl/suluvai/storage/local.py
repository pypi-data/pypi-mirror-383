"""
Local filesystem storage (uses suluvai.storage.local_storage.LocalFileStorage)
"""

from suluvai.storage.local_storage import LocalFileStorage

# Re-export for cleaner imports
LocalStorage = LocalFileStorage

__all__ = ["LocalStorage"]
