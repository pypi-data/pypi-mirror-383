"""
Zone parser
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
from typing import List, Optional
from ..core.models import Zone
from .base import BaseParser

def parse_zone(filename: str, loader) -> List[Zone]:
    """
    Parse zone file.
    
    Args:
        filename: File to parse
        loader: File loader instance
        
    Returns:
        List of Zone objects
    """
    if not loader.file_exists(filename):
        return []
    
    lines = loader.load_file(filename)
    return _parse_zone_lines(lines, filename)

def parse_zone_line(line: str, region: Optional[str] = None, line_number: Optional[int] = None) -> Optional[Zone]:
    """
    Parse single zone line.
    
    Args:
        line: Line to parse
        region: Region name
        line_number: Line number in file
        
    Returns:
        Zone object or None if not a zone line
    """
    parts = BaseParser.split_line(line)
    if not parts or parts[0] != 'Zone':
        return None
    
    if len(parts) < 5:
        return None
    
    return Zone(
        name=parts[1],
        offset=parts[2],
        rules=parts[3],
        format=parts[4],
        until=parts[5] if len(parts) > 5 else None,
        region=region,
        line_number=line_number
    )

def _parse_zone_lines(lines: List[str], region: str) -> List[Zone]:
    """
    Parse multiple zone lines from file content.
    
    Args:
        lines: File lines
        region: Region name
        
    Returns:
        List of Zone objects
    """
    zones = []
    current_zone = None
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Handle continuation lines (indented)
        if line.startswith(' ') or line.startswith('\t'):
            if current_zone:
                # Add current zone before starting continuation
                zones.append(current_zone)
                # Parse continuation as new zone with same name
                cont_parts = BaseParser.split_line(line.strip())
                if len(cont_parts) >= 3:
                    current_zone = Zone(
                        name=current_zone.name,
                        offset=cont_parts[0],
                        rules=cont_parts[1],
                        format=cont_parts[2],
                        until=cont_parts[3] if len(cont_parts) > 3 else None,
                        region=region,
                        line_number=line_num
                    )
        else:
            # New declaration
            if current_zone:
                zones.append(current_zone)
            
            zone = parse_zone_line(line, region, line_num)
            if zone:
                current_zone = zone
            else:
                current_zone = None
    
    # Don't forget the last zone
    if current_zone:
        zones.append(current_zone)
    
    return zones