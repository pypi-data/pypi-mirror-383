"""
Base parser with common utilities
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
import re
from typing import List, Optional

class BaseParser:
    """Base parser with common functionality"""
    
    @staticmethod
    def split_line(line: str) -> List[str]:
        """
        Split line while handling comments and preserving structure.
        
        Args:
            line: Input line
            
        Returns:
            List of parts
        """
        # Remove inline comments
        line = re.sub(r'#.*$', '', line).strip()
        if not line:
            return []
        
        # Split on whitespace, handling quoted strings
        parts = []
        current_part = []
        in_quotes = False
        quote_char = None
        
        for char in line:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current_part.append(char)
            elif char.isspace() and not in_quotes:
                if current_part:
                    parts.append(''.join(current_part))
                    current_part = []
            else:
                current_part.append(char)
        
        if current_part:
            parts.append(''.join(current_part))
        
        return parts
    
    @staticmethod
    def parse_offset(offset_str: str) -> Optional[float]:
        """
        Parse timezone offset string to hours.
        
        Args:
            offset_str: Offset string (e.g., "-5:00", "1:30")
            
        Returns:
            Offset in hours or None if invalid
        """
        if not offset_str or offset_str == '-':
            return 0.0
        
        # Handle negative offsets
        sign = -1 if offset_str.startswith('-') else 1
        offset_str = offset_str.lstrip('+-')
        
        # Parse hours, minutes, seconds
        parts = offset_str.split(':')
        try:
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            seconds = int(parts[2]) if len(parts) > 2 else 0
            
            total_hours = hours + minutes/60 + seconds/3600
            return sign * total_hours
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def parse_time(time_str: str) -> Optional[float]:
        """
        Parse time string to hours since midnight.
        
        Args:
            time_str: Time string (e.g., "2:00", "14:30:45")
            
        Returns:
            Hours since midnight or None if invalid
        """
        if not time_str:
            return 0.0
        
        # Remove time modifiers
        time_str = re.sub(r'[wsug]$', '', time_str)
        
        parts = time_str.split(':')
        try:
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            seconds = int(parts[2]) if len(parts) > 2 else 0
            
            return hours + minutes/60 + seconds/3600
        except (ValueError, IndexError):
            return None