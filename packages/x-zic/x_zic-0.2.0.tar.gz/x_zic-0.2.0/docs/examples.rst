Examples
========

This section provides practical examples and recipes for common timezone tasks.

Basic Examples
--------------

Find All DST-Observing Zones
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from x_zic import read_zones

    zones = read_zones()
    dst_zones = [
        zone for zone in zones 
        if zone['rules'] not in ['-', '', None]
    ]
    print(f"Found {len(dst_zones)} DST-observing zones")

Calculate Offset Changes
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from x_zic import get_transitions

    transitions = get_transitions('Europe/London', 2023, 2024)
    for t in transitions:
        change = "DST Start" if t['is_dst'] else "DST End"
        print(f"{t['timestamp'][:10]}: {change} ({t['abbrev']})")

Geographic Queries
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from x_zic.geo import read_zonetab

    geo_zones = read_zonetab()
    us_zones = [z for z in geo_zones if z['country_code'] == 'US']

    for zone in us_zones:
        print(f"{zone['zone_id']} - {zone['comments']}")

Advanced Examples
-----------------

Timezone Statistics
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from x_zic import read_zones
    from collections import Counter

    zones = read_zones()
    
    # Count by region
    region_counts = Counter(zone['region'] for zone in zones)
    print("Zones by region:")
    for region, count in region_counts.most_common():
        print(f"  {region}: {count}")
    
    # Count DST usage
    dst_count = sum(1 for zone in zones if zone['rules'] not in ['-', ''])
    print(f"DST zones: {dst_count}/{len(zones)} ({dst_count/len(zones)*100:.1f}%)")

Transition Analysis
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from x_zic import get_transitions
    from datetime import datetime

    def analyze_transitions(zone_name, years=5):
        end_year = datetime.now().year
        start_year = end_year - years
        
        transitions = get_transitions(zone_name, start_year, end_year)
        
        print(f"Transition analysis for {zone_name} ({start_year}-{end_year}):")
        print(f"Total transitions: {len(transitions)}")
        
        dst_starts = [t for t in transitions if t['is_dst']]
        dst_ends = [t for t in transitions if not t['is_dst']]
        
        print(f"DST starts: {len(dst_starts)}")
        print(f"DST ends: {len(dst_ends)}")
        
        if dst_starts:
            avg_start = sum(int(t['timestamp'][5:7]) for t in dst_starts) / len(dst_starts)
            print(f"Average DST start month: {avg_start:.1f}")
        
        return transitions

    # Usage
    transitions = analyze_transitions('America/New_York')

Timezone Conversion Utility
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from x_zic import get_transitions
    from datetime import datetime, timedelta

    class TimezoneConverter:
        def __init__(self, zone_name):
            self.zone_name = zone_name
            self.transitions = get_transitions(zone_name, 1970, 2030)
        
        def utc_to_local(self, utc_dt):
            """Convert UTC datetime to local time"""
            # Find applicable transition
            for i, transition in enumerate(self.transitions):
                trans_dt = datetime.fromisoformat(transition['timestamp'])
                if utc_dt < trans_dt:
                    # Use previous transition's offset
                    if i > 0:
                        prev_trans = self.transitions[i-1]
                        offset = self._parse_offset(prev_trans['offset_after'])
                    else:
                        offset = self._parse_offset(transition['offset_before'])
                    return utc_dt + timedelta(hours=offset)
            
            # Use last transition's offset
            if self.transitions:
                last_trans = self.transitions[-1]
                offset = self._parse_offset(last_trans['offset_after'])
                return utc_dt + timedelta(hours=offset)
            
            return utc_dt
        
        def _parse_offset(self, offset_str):
            """Parse offset string to hours"""
            # Simplified offset parsing
            if offset_str.startswith('-'):
                return -int(offset_str[1:3])
            else:
                return int(offset_str[:2])

    # Usage
    converter = TimezoneConverter('America/Los_Angeles')
    utc_time = datetime(2024, 3, 10, 12, 0, 0)
    local_time = converter.utc_to_local(utc_time)
    print(f"UTC: {utc_time} -> Local: {local_time}")

Integration Examples
--------------------

With FastAPI Web Service
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from fastapi import FastAPI, HTTPException
    from x_zic import read_zones, get_transitions

    app = FastAPI(title="Timezone API")

    @app.get("/zones")
    async def list_zones(region: str = None):
        """List all timezones or filter by region"""
        try:
            zones = read_zones(region)
            return {"zones": zones}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/zones/{zone_name}/transitions")
    async def get_zone_transitions(zone_name: str, start_year: int = 2020, end_year: int = 2030):
        """Get transitions for a specific zone"""
        try:
            transitions = get_transitions(zone_name, start_year, end_year)
            return {
                "zone": zone_name,
                "transitions": transitions
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

With Pandas Analysis
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import pandas as pd
    from x_zic import read_zones, get_transitions

    # Comprehensive timezone analysis
    zones = read_zones()
    df_zones = pd.DataFrame(zones)

    # Basic statistics
    print("Timezone Analysis Report")
    print("=" * 50)
    print(f"Total zones: {len(df_zones)}")
    print(f"Regions: {df_zones['region'].nunique()}")
    print(f"DST zones: {len(df_zones[df_zones['rules'] != '-'])}")

    # Region analysis
    region_stats = df_zones['region'].value_counts()
    print("\nZones by region:")
    for region, count in region_stats.items():
        print(f"  {region:15} {count:3} zones")

    # Offset analysis
    def extract_offset_hours(offset_str):
        if offset_str == '-' or not offset_str:
            return 0
        try:
            sign = -1 if offset_str.startswith('-') else 1
            parts = offset_str.replace('-', '').replace('+', '').split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return sign * (hours + minutes/60)
        except:
            return 0

    df_zones['offset_hours'] = df_zones['offset'].apply(extract_offset_hours)
    print(f"\nOffset range: {df_zones['offset_hours'].min():.1f} to {df_zones['offset_hours'].max():.1f} hours")

Real-world Use Cases
--------------------

1. **Scheduling System**: Calculate local times for international meetings
2. **Data Analysis**: Analyze timezone distribution for global user base
3. **Monitoring**: Track DST transitions for system alerts
4. **Migration Tool**: Convert historical timestamps between timezones
5. **API Service**: Provide timezone information to other applications

Troubleshooting
---------------

Common Issues
^^^^^^^^^^^^^

**Problem**: Zone not found
**Solution**: Check for typos and use `x_zic.read_zones()` to see available zones

**Problem**: Cache issues  
**Solution**: Use `x_zic.clear_cache()` to reset

**Problem**: Performance problems
**Solution**: Enable caching and load only needed regions

Need more help? Check the :doc:`api-reference` for detailed API documentation.