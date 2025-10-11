"""
Rule parser
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
from ..core.models import Rule
from .base import BaseParser

def parse_rule(filename: str, loader) -> List[Rule]:
    """
    Parse rule file.
    
    Args:
        filename: File to parse
        loader: File loader instance
        
    Returns:
        List of Rule objects
    """
    if not loader.file_exists(filename):
        return []
    
    lines = loader.load_file(filename)
    return _parse_rule_lines(lines, filename)

def parse_rule_line(line: str, region: Optional[str] = None, line_number: Optional[int] = None) -> Optional[Rule]:
    """
    Parse single rule line.
    
    Args:
        line: Line to parse
        region: Region name
        line_number: Line number in file
        
    Returns:
        Rule object or None if not a rule line
    """
    parts = BaseParser.split_line(line)
    if not parts or parts[0] != 'Rule':
        return None
    
    if len(parts) < 9:
        return None
    
    # Parse year range
    from_year = int(parts[2])
    to_year = parts[3]
    if to_year != 'max':
        try:
            to_year = int(to_year)
        except ValueError:
            pass  # Keep as string if not numeric
    
    return Rule(
        name=parts[1],
        from_year=from_year,
        to_year=to_year,
        type=parts[4],
        month=parts[5],
        day=parts[6],
        time=parts[7],
        save=parts[8],
        letter=parts[9] if len(parts) > 9 else '',
        region=region,
        line_number=line_number
    )

def _parse_rule_lines(lines: List[str], region: str) -> List[Rule]:
    """
    Parse multiple rule lines from file content.
    
    Args:
        lines: File lines
        region: Region name
        
    Returns:
        List of Rule objects
    """
    rules = []
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        if not line or line.startswith('#'):
            continue
        
        rule = parse_rule_line(line, region, line_num)
        if rule:
            rules.append(rule)
    
    return rules