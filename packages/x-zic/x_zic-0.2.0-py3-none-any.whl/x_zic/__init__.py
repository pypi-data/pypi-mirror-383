"""
x-zic - TZDB Parser
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

from .core.loader import FileLoader
from .core.config import TZDBConfig
from .parser import parse_zone, parse_rule, parse_link, parse_leap
from .transitions import get_transitions

try:
    from ._version import __version__
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
    """Read all zones or zones from specific region."""
    loader = _get_loader()
    
    if region:
        from .regions import get_zones_by_region
        return get_zones_by_region(region, loader)
    else:
        zones = []
        from .regions import list_regions
        for reg in list_regions():
            zones.extend(get_zones_by_region(reg, loader))
        return zones

def parse_zone_file(filename):
    """Parse specific zone file."""
    loader = _get_loader()
    return parse_zone(filename, loader)

def get_transitions(zone_name, start_year=1970, end_year=2030):
    """Get timezone transitions for a zone."""
    from .transitions import get_transitions as get_transitions_impl
    return get_transitions_impl(zone_name, start_year, end_year, _get_loader())

def parse_leap_seconds(filename="leapseconds"):
    """
    Parse leap seconds file.
    
    Args:
        filename: Name of leap seconds file to parse
        
    Returns:
        List of leap second dictionaries
    """
    loader = _get_loader()
    leap_seconds = parse_leap(filename, loader)
    from .parser.leap import calculate_cumulative_offsets
    leap_seconds = calculate_cumulative_offsets(leap_seconds)
    return [ls.to_dict() for ls in leap_seconds]

def clear_cache():
    """Clear all cached data"""
    global _loader
    if _loader:
        _loader.clear_cache()
    _loader = None