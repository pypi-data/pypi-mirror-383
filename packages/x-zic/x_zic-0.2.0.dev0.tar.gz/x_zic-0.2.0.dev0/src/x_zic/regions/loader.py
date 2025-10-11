"""
Region file loader
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
from typing import List, Dict, Any
from ..parser import parse_zone, parse_rule, parse_link
from ..core.config import TZDBConfig

def list_regions() -> List[str]:
    """Get list of all region names"""
    config = TZDBConfig()
    return config.region_files

def get_zones_by_region(region: str, loader) -> List[Dict[str, Any]]:
    """
    Get all zones from a region.
    
    Args:
        region: Region name
        loader: File loader
        
    Returns:
        List of zone dictionaries
    """
    zones = parse_zone(region, loader)
    return [zone.to_dict() for zone in zones]

def get_rules_by_region(region: str, loader) -> List[Dict[str, Any]]:
    """
    Get all rules from a region.
    
    Args:
        region: Region name
        loader: File loader
        
    Returns:
        List of rule dictionaries
    """
    rules = parse_rule(region, loader)
    return [rule.to_dict() for rule in rules]

def get_links_by_region(region: str, loader) -> List[Dict[str, Any]]:
    """
    Get all links from a region.
    
    Args:
        region: Region name
        loader: File loader
        
    Returns:
        List of link dictionaries
    """
    links = parse_link(region, loader)
    return [link.to_dict() for link in links]