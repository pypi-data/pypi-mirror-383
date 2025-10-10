"""
Transition calculator - core DST logic
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from ..core.models import Zone, Rule
from ..parser.base import BaseParser

def get_transitions(zone_name: str, start_year: int = 1970, end_year: int = 2030, loader = None) -> List[Dict[str, Any]]:
    """
    Calculate transitions for a zone.
    
    Args:
        zone_name: Zone identifier
        start_year: Start year
        end_year: End year
        loader: File loader
        
    Returns:
        List of transition dictionaries
    """
    # This is a simplified implementation
    # Full implementation would:
    # 1. Find the zone definition
    # 2. Find applicable rules
    # 3. Calculate transition dates for each year
    # 4. Convert to UTC timestamps
    
    # Placeholder implementation
    transitions = []
    
    # Mock some transitions for common zones
    if "New_York" in zone_name:
        # Mock DST transitions for New York
        for year in range(start_year, end_year + 1):
            # Spring forward (2nd Sunday in March)
            spring_date = _find_nth_weekday(year, 3, 2, 6)  # 2nd Sunday
            transitions.append({
                'zone': zone_name,
                'timestamp': datetime(year, 3, spring_date, 2, 0, 0).isoformat(),
                'offset_before': '-05:00',
                'offset_after': '-04:00',
                'is_dst': True,
                'abbrev': 'EDT'
            })
            
            # Fall back (1st Sunday in November)
            fall_date = _find_nth_weekday(year, 11, 1, 6)  # 1st Sunday
            transitions.append({
                'zone': zone_name,
                'timestamp': datetime(year, 11, fall_date, 2, 0, 0).isoformat(),
                'offset_before': '-04:00',
                'offset_after': '-05:00',
                'is_dst': False,
                'abbrev': 'EST'
            })
    
    return sorted(transitions, key=lambda x: x['timestamp'])

def _find_nth_weekday(year: int, month: int, n: int, weekday: int) -> int:
    """
    Find the nth weekday in a month.
    
    Args:
        year: Year
        month: Month (1-12)
        n: Which occurrence (1=first, 2=second, etc.)
        weekday: Weekday (0=Monday, 6=Sunday)
        
    Returns:
        Day of month
    """
    # Find first day of the month
    first_day = datetime(year, month, 1)
    
    # Find first occurrence of the weekday
    days_to_add = (weekday - first_day.weekday()) % 7
    first_occurrence = first_day.day + days_to_add
    
    # Calculate nth occurrence
    target_day = first_occurrence + (n - 1) * 7
    
    # Check if still in same month
    try:
        datetime(year, month, target_day)
        return target_day
    except ValueError:
        return target_day - 7  # Use last occurrence if out of bounds

def calculate_dst_transitions(zone: Zone, rules: List[Rule], year: int) -> List[Dict[str, Any]]:
    """
    Calculate DST transitions for a zone in a specific year.
    
    Args:
        zone: Zone definition
        rules: Applicable rules
        year: Year to calculate
        
    Returns:
        List of transition dictionaries
    """
    transitions = []
    
    for rule in rules:
        if not _rule_applies(rule, year):
            continue
        
        # Calculate transition date
        transition_date = _calculate_rule_date(rule, year)
        if transition_date:
            transitions.append({
                'date': transition_date,
                'rule': rule,
                'zone': zone
            })
    
    return transitions

def _rule_applies(rule: Rule, year: int) -> bool:
    """Check if rule applies to given year"""
    if rule.to_year == 'max':
        return year >= rule.from_year
    else:
        return rule.from_year <= year <= rule.to_year

def _calculate_rule_date(rule: Rule, year: int) -> Optional[datetime]:
    """Calculate actual date for rule transition"""
    try:
        month = _month_to_number(rule.month)
        day = _parse_day_spec(rule.day, year, month)
        
        if day:
            return datetime(year, month, day)
    except (ValueError, KeyError):
        pass
    
    return None

def _month_to_number(month: str) -> int:
    """Convert month name to number"""
    months = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    return months[month]

def _parse_day_spec(day_spec: str, year: int, month: int) -> Optional[int]:
    """Parse day specification like 'Sun>=8', 'lastSun', '15'"""
    if day_spec.isdigit():
        return int(day_spec)
    
    # Handle lastSun, lastMon, etc.
    if day_spec.startswith('last'):
        weekday = _weekday_to_number(day_spec[4:])
        return _find_last_weekday(year, month, weekday)
    
    # Handle Sun>=8, Sun<=25, etc.
    match = re.match(r'(\w{3})([<>]=)?(\d+)', day_spec)
    if match:
        weekday_name, comparator, day_num = match.groups()
        weekday = _weekday_to_number(weekday_name)
        base_day = int(day_num)
        
        if comparator == '>=':
            return _find_weekday_on_or_after(year, month, base_day, weekday)
        elif comparator == '<=':
            return _find_weekday_on_or_before(year, month, base_day, weekday)
    
    return None

def _weekday_to_number(weekday: str) -> int:
    """Convert weekday name to number (0=Monday, 6=Sunday)"""
    weekdays = {
        'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3,
        'Fri': 4, 'Sat': 5, 'Sun': 6
    }
    return weekdays[weekday]

def _find_last_weekday(year: int, month: int, weekday: int) -> int:
    """Find last occurrence of weekday in month"""
    # Start from last day of month
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Go backwards to find the weekday
    days_back = (last_day.weekday() - weekday) % 7
    return last_day.day - days_back

def _find_weekday_on_or_after(year: int, month: int, day: int, weekday: int) -> int:
    """Find first weekday on or after given day"""
    base_date = datetime(year, month, day)
    days_to_add = (weekday - base_date.weekday()) % 7
    return base_date.day + days_to_add

def _find_weekday_on_or_before(year: int, month: int, day: int, weekday: int) -> int:
    """Find last weekday on or before given day"""
    base_date = datetime(year, month, day)
    days_to_subtract = (base_date.weekday() - weekday) % 7
    return base_date.day - days_to_subtract