"""
Link parser
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
from ..core.models import Link
from .base import BaseParser

def parse_link(filename: str, loader) -> List[Link]:
    """
    Parse link file.
    
    Args:
        filename: File to parse
        loader: File loader instance
        
    Returns:
        List of Link objects
    """
    if not loader.file_exists(filename):
        return []
    
    lines = loader.load_file(filename)
    return _parse_link_lines(lines, filename)

def parse_link_line(line: str, region: Optional[str] = None, line_number: Optional[int] = None) -> Optional[Link]:
    """
    Parse single link line.
    
    Args:
        line: Line to parse
        region: Region name
        line_number: Line number in file
        
    Returns:
        Link object or None if not a link line
    """
    parts = BaseParser.split_line(line)
    if not parts or parts[0] != 'Link':
        return None
    
    if len(parts) < 3:
        return None
    
    return Link(
        target=parts[1],
        alias=parts[2],
        region=region
    )

def _parse_link_lines(lines: List[str], region: str) -> List[Link]:
    """
    Parse multiple link lines from file content.
    
    Args:
        lines: File lines
        region: Region name
        
    Returns:
        List of Link objects
    """
    links = []
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        if not line or line.startswith('#'):
            continue
        
        link = parse_link_line(line, region)
        if link:
            links.append(link)
    
    return links