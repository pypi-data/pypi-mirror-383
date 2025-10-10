"""
Link parser
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