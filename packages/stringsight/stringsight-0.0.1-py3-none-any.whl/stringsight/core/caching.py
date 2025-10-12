"""
Disk-backed caching for LLM responses and embeddings using DiskCache.
"""

import json
import hashlib
import numpy as np
import re
from pathlib import Path
from typing import Optional, Dict, Any, Union
from diskcache import Cache as DiskCache

def parse_size_string(size_str: str) -> int:
    """Parse a size string like '10GB' or '1TB' into bytes."""
    if isinstance(size_str, int):
        return size_str
    
    # Remove any whitespace and convert to uppercase
    size_str = size_str.strip().upper()
    
    # Match pattern like "10GB", "1.5TB", etc.
    match = re.match(r'^(\d+(?:\.\d+)?)\s*(B|KB|MB|GB|TB)$', size_str)
    if not match:
        raise ValueError(f"Invalid size string: {size_str}. Expected format like '10GB' or '1TB'")
    
    number = float(match.group(1))
    unit = match.group(2)
    
    # Convert to bytes
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    
    return int(number * multipliers[unit])

class Cache:
    def __init__(self, cache_dir: str = ".cache/stringsight", max_size: Union[str, int] = "50GB"):
        """Initialize DiskCache-backed cache.
        
        Args:
            cache_dir: Base directory to store cache files
            max_size: Max on-disk cache size in bytes or size string like "50GB"
        """
        import os
        self.cache_dir = Path(os.environ.get("STRINGSIGHT_CACHE_DIR", cache_dir))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(max_size, str):
            env_size = os.environ.get("STRINGSIGHT_CACHE_MAX_SIZE", max_size)
            size_limit = parse_size_string(env_size)
        else:
            size_limit = int(max_size)
        
        # Separate namespaces for completions and embeddings
        self._completions = DiskCache(str(self.cache_dir / "completions"), size_limit=size_limit)
        self._embeddings = DiskCache(str(self.cache_dir / "embeddings"), size_limit=size_limit)

    def _get_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate deterministic cache key from input data."""
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def get_completion(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached completion response."""
        key = self._get_cache_key(request_data)
        value = self._completions.get(key)
        if value is not None:
            # Stored as JSON-serializable dict
            return value
        return None

    def set_completion(self, request_data: Dict[str, Any], response_data: Dict[str, Any]) -> None:
        """Cache completion response."""
        key = self._get_cache_key(request_data)
        # Store as Python object (DiskCache pickles by default)
        self._completions.set(key, response_data)

    def get_embedding(self, text: Union[str, list]) -> Optional[np.ndarray]:
        """Get cached embedding."""
        key = self._get_cache_key({"text": text})
        value = self._embeddings.get(key)
        if value is None:
            return None
        if isinstance(value, bytes):
            return np.frombuffer(value, dtype=np.float32)
        if isinstance(value, np.ndarray):
            return value
        # Fallback: list -> ndarray
        try:
            return np.array(value, dtype=np.float32)
        except Exception:
            return None

    def set_embedding(self, text: Union[str, list], embedding: np.ndarray) -> None:
        """Cache embedding."""
        key = self._get_cache_key({"text": text})
        value = np.array(embedding, dtype=np.float32).tobytes()
        self._embeddings.set(key, value)

    def close(self):
        """Close DiskCache stores."""
        try:
            self._completions.close()
        finally:
            self._embeddings.close()