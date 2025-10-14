"""
Storage backends for SuluvAI
"""

from suluvai.storage.virtual import VirtualStorage
from suluvai.storage.local import LocalStorage
from suluvai.storage.hybrid import HybridStorage

__all__ = ["VirtualStorage", "LocalStorage", "HybridStorage"]
