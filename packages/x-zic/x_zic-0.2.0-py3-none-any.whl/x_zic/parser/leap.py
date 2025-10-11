"""
Leap second parser
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
from datetime import datetime
from typing import List, Optional
from ..core.models import LeapSecond
from .base import BaseParser


def parse_leap(filename: str, loader) -> List[LeapSecond]:
    """
    Parse leap seconds file.
    
    Args:
        filename: File to parse
        loader: File loader instance
        
    Returns:
        List of LeapSecond objects
    """
    if not loader.file_exists(filename):
        return []
    
    lines = loader.load_file(filename)
    return _parse_leap_lines(lines, filename)


def parse_leap_line(line: str, source: Optional[str] = None, line_number: Optional[int] = None) -> Optional[LeapSecond]:
    """
    Parse single leap second line.
    
    Args:
        line: Line to parse
        source: Source file name
        line_number: Line number in file
        
    Returns:
        LeapSecond object or None if not a leap second line
    """
    parts = BaseParser.split_line(line)
    
    # Try tzdb format first: "Leap YEAR MON DAY TIME CORR [R/S]"
    if parts and parts[0] == 'Leap':
        return _parse_tzdb_leap_line(parts, source, line_number)
    
    # Try NIST format: "NTP_TIMESTAMP TAI-UTC"
    elif parts and len(parts) >= 2 and parts[0].isdigit():
        return _parse_nist_leap_line(parts, source, line_number)
    
    return None


def _parse_tzdb_leap_line(parts: List[str], source: Optional[str] = None, line_number: Optional[int] = None) -> Optional[LeapSecond]:
    """
    Parse tzdb format leap second line.
    
    Format: "Leap YEAR MON DAY TIME CORR [R/S]"
    Example: "Leap 1972 Jun 30 23:59:60 + S"
    
    Args:
        parts: Split line parts
        source: Source file name
        line_number: Line number in file
        
    Returns:
        LeapSecond object or None if invalid
    """
    if len(parts) < 6:
        return None
    
    try:
        year = int(parts[1])
        month_name = parts[2]
        day = int(parts[3])
        time_str = parts[4]
        correction = parts[5]
        
        # Convert month name to number
        month = _month_name_to_number(month_name)
        if month is None:
            return None
        
        # Parse time
        time_parts = time_str.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        # Create datetime and timestamp
        leap_date = datetime(year, month, day, hour, minute, second)
        timestamp = int(leap_date.timestamp())
        
        # Calculate total offset (this is simplified - would need cumulative calculation)
        # For now, we'll set this to None and calculate it in a separate function
        total_offset = None
        
        return LeapSecond(
            timestamp=timestamp,
            total_offset=total_offset,
            date=leap_date.strftime('%Y-%m-%d')
        )
        
    except (ValueError, IndexError, KeyError):
        return None


def _parse_nist_leap_line(parts: List[str], source: Optional[str] = None, line_number: Optional[int] = None) -> Optional[LeapSecond]:
    """
    Parse NIST format leap second line.
    
    Format: "NTP_TIMESTAMP TAI-UTC [EXPIRATION]"
    Example: "2272060800 10  # 1 Jan 1972"
    
    Args:
        parts: Split line parts
        source: Source file name
        line_number: Line number in file
        
    Returns:
        LeapSecond object or None if invalid
    """
    if len(parts) < 2:
        return None
    
    try:
        ntp_timestamp = int(parts[0])
        total_offset = int(parts[1])
        
        # Convert NTP timestamp to Unix timestamp
        # NTP epoch: 1900-01-01, Unix epoch: 1970-01-01
        # Difference: 2208988800 seconds
        unix_timestamp = ntp_timestamp - 2208988800
        
        # Create date string
        leap_date = datetime.fromtimestamp(unix_timestamp)
        
        return LeapSecond(
            timestamp=unix_timestamp,
            total_offset=total_offset,
            date=leap_date.strftime('%Y-%m-%d')
        )
        
    except (ValueError, IndexError):
        return None


def _parse_leap_lines(lines: List[str], source: str) -> List[LeapSecond]:
    """
    Parse multiple leap second lines from file content.
    
    Args:
        lines: File lines
        source: Source file name
        
    Returns:
        List of LeapSecond objects
    """
    leap_seconds = []
    total_offset = 10  # Initial TAI-UTC offset before 1972
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        if not line or line.startswith('#'):
            continue
        
        leap_second = parse_leap_line(line, source, line_num)
        if leap_second:
            # Calculate cumulative offset for tzdb format
            if leap_second.total_offset is None:
                # This is a simplified approach - in real implementation,
                # you'd need to track the cumulative offset
                parts = BaseParser.split_line(line)
                if len(parts) >= 6 and parts[5] == '+':
                    total_offset += 1
                elif len(parts) >= 6 and parts[5] == '-':
                    total_offset -= 1
                leap_second.total_offset = total_offset
            
            leap_seconds.append(leap_second)
    
    return leap_seconds


def _month_name_to_number(month_name: str) -> Optional[int]:
    """
    Convert month name to number.
    
    Args:
        month_name: Month name (e.g., 'Jan', 'Feb')
        
    Returns:
        Month number (1-12) or None if invalid
    """
    months = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    return months.get(month_name)


def calculate_cumulative_offsets(leap_seconds: List[LeapSecond]) -> List[LeapSecond]:
    """
    Calculate cumulative TAI-UTC offsets for leap seconds.
    
    This function processes leap seconds in chronological order and
    calculates the cumulative TAI-UTC offset for each entry.
    
    Args:
        leap_seconds: List of leap seconds (may not have cumulative offsets)
        
    Returns:
        List of leap seconds with cumulative offsets calculated
    """
    if not leap_seconds:
        return []
    
    # Sort by timestamp
    sorted_leap_seconds = sorted(leap_seconds, key=lambda x: x.timestamp)
    
    # Initial offset before any leap seconds
    cumulative_offset = 10  # TAI-UTC was 10 seconds before 1972
    
    result = []
    for leap in sorted_leap_seconds:
        # If this leap second already has an offset, use it
        if leap.total_offset is not None:
            cumulative_offset = leap.total_offset
        else:
            # This is where we'd calculate based on the leap second data
            # For now, we'll increment based on typical pattern
            cumulative_offset += 1
        
        result.append(LeapSecond(
            timestamp=leap.timestamp,
            total_offset=cumulative_offset,
            date=leap.date
        ))
    
    return result