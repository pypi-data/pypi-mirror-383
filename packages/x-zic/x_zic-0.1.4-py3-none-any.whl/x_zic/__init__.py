"""
TZDB Parser - Production-ready timezone database parser
"""

from .core.loader import FileLoader
from .core.config import TZDBConfig
from .parser import parse_zone, parse_rule, parse_link
from .transitions import get_transitions

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.1.0"

__all__ = [
    "read_zones", 
    "parse_zone", 
    "get_transitions", 
    "clear_cache",
    "FileLoader",
    "TZDBConfig",
    "__version__",
]

# Global cache
_config = None
_loader = None

def _get_loader():
    """Initialize loader with default config"""
    global _config, _loader
    if _loader is None:
        _config = TZDBConfig()
        _loader = FileLoader(_config)
    return _loader

def read_zones(region=None):
    """
    Read all zones or zones from specific region.
    
    Args:
        region: Optional region name (e.g., 'europe', 'asia')
    
    Returns:
        List of zone dictionaries
    """
    loader = _get_loader()
    
    if region:
        from .regions import get_zones_by_region
        return get_zones_by_region(region, loader)
    else:
        # Load all zones
        zones = []
        from .regions import list_regions
        for reg in list_regions():
            zones.extend(get_zones_by_region(reg, loader))
        return zones

def parse_zone_file(filename):
    """
    Parse specific zone file.
    
    Args:
        filename: Name of file to parse
        
    Returns:
        List of parsed zone entries
    """
    loader = _get_loader()
    return parse_zone(filename, loader)

def get_transitions(zone_name, start_year=1970, end_year=2030):
    """
    Get timezone transitions for a zone.
    
    Args:
        zone_name: Zone identifier (e.g., 'America/New_York')
        start_year: Starting year
        end_year: Ending year
        
    Returns:
        List of transition dictionaries
    """
    from .transitions import get_transitions as get_transitions_impl
    return get_transitions_impl(zone_name, start_year, end_year, _get_loader())

def clear_cache():
    """Clear all cached data"""
    global _loader
    if _loader:
        _loader.clear_cache()
    _loader = None