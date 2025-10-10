"""
Configuration and constants
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass
class TZDBConfig:
    """Configuration for TZDB parser"""
    
    # Paths
    tzdb_source_path: str = "tzdb-2025b"
    cache_dir: str = ".tzdb_cache"
    
    # Cache settings
    cache_enabled: bool = True
    cache_version: str = "1.0"
    
    # Performance
    max_transition_years: int = 100
    
    # File groups
    region_files: List[str] = None
    legacy_files: List[str] = None
    geo_files: List[str] = None
    
    def __post_init__(self):
        if self.region_files is None:
            self.region_files = [
                "africa", "antarctica", "asia", "australasia",
                "europe", "northamerica", "southamerica", "etcetera", "factory"
            ]
        
        if self.legacy_files is None:
            self.legacy_files = ["backward", "backzone"]
        
        if self.geo_files is None:
            self.geo_files = ["zone.tab", "zone1970.tab", "iso3166.tab"]

# Constants
MONTHS = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Regex patterns
OFFSET_PATTERN = r'([+-]?)(\d{1,2}):?(\d{2})?(:?(\d{2}))?'
TIME_PATTERN = r'(\d{1,2}):?(\d{2})?(:?(\d{2}))?([wsug]?)'
DAY_PATTERN = r'^(last|first)?(\w{3})([<>]=)?(\d+)?$'