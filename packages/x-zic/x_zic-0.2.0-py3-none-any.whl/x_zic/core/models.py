"""
Data models for TZDB entities
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

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class Zone:
    """Timezone zone definition"""
    name: str
    offset: str
    rules: str
    format: str
    until: Optional[str] = None
    region: Optional[str] = None
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'offset': self.offset,
            'rules': self.rules,
            'format': self.format,
            'until': self.until,
            'region': self.region,
            'line_number': self.line_number
        }

@dataclass
class Rule:
    """DST rule definition"""
    name: str
    from_year: int
    to_year: str  # "max" or year
    type: str
    month: str
    day: str
    time: str
    save: str
    letter: str
    region: Optional[str] = None
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'from_year': self.from_year,
            'to_year': self.to_year,
            'type': self.type,
            'month': self.month,
            'day': self.day,
            'time': self.time,
            'save': self.save,
            'letter': self.letter,
            'region': self.region,
            'line_number': self.line_number
        }

@dataclass
class Link:
    """Timezone link/alias"""
    target: str
    alias: str
    region: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'target': self.target,
            'alias': self.alias,
            'region': self.region
        }

@dataclass
class Transition:
    """Timezone transition"""
    zone: str
    timestamp: datetime
    offset_before: str
    offset_after: str
    is_dst: bool
    abbrev: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'zone': self.zone,
            'timestamp': self.timestamp.isoformat(),
            'offset_before': self.offset_before,
            'offset_after': self.offset_after,
            'is_dst': self.is_dst,
            'abbrev': self.abbrev
        }

@dataclass
class LeapSecond:
    """Leap second definition"""
    timestamp: int
    total_offset: int
    date: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'total_offset': self.total_offset,
            'date': self.date
        }