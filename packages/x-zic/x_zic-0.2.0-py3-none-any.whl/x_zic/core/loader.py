"""
File loading with caching
Copyright (C) 2024 Your Name

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from .config import TZDBConfig

class FileLoader:
    """Smart file loader with caching"""
    
    def __init__(self, config: TZDBConfig):
        self.config = config
        self._file_cache: Dict[str, List[str]] = {}
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if needed"""
        if self.config.cache_enabled:
            Path(self.config.cache_dir).mkdir(exist_ok=True)
    
    def _get_cache_key(self, filename: str) -> str:
        """Generate cache key for file"""
        return f"{self.config.cache_version}_{filename}"
    
    def _get_cache_path(self, filename: str) -> str:
        """Get cache file path"""
        return os.path.join(self.config.cache_dir, f"{self._get_cache_key(filename)}.json")
    
    def load_file(self, filename: str, use_cache: bool = True) -> List[str]:
        """
        Load file with optional caching.
        
        Args:
            filename: File to load
            use_cache: Use cache if available
            
        Returns:
            List of file lines
        """
        # Check memory cache first
        if filename in self._file_cache:
            return self._file_cache[filename]
        
        # Check disk cache
        cache_path = self._get_cache_path(filename)
        if use_cache and self.config.cache_enabled and os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                lines = cached_data.get('lines', [])
                self._file_cache[filename] = lines
                return lines
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Load from source
        filepath = os.path.join(self.config.tzdb_source_path, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"TZDB file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f]
        
        # Cache in memory
        self._file_cache[filename] = lines
        
        # Cache to disk
        if use_cache and self.config.cache_enabled:
            cache_data = {
                'filename': filename,
                'lines': lines,
                'version': self.config.cache_version
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        
        return lines
    
    def file_exists(self, filename: str) -> bool:
        """Check if file exists in source directory"""
        filepath = os.path.join(self.config.tzdb_source_path, filename)
        return os.path.exists(filepath)
    
    def clear_cache(self):
        """Clear all cached data"""
        self._file_cache.clear()
        if os.path.exists(self.config.cache_dir):
            import shutil
            shutil.rmtree(self.config.cache_dir)
        self._ensure_cache_dir()