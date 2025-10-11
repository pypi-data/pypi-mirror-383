# TZDB Parser

A high-performance Python library for parsing and analyzing the IANA Time Zone Database (tzdb). Built for production use with smart caching, minimal dependencies, and a practical API.

## Features

- 🚀 **Blazing Fast**: Smart caching system for instant subsequent loads
- 📦 **Zero Dependencies**: Pure Python standard library
- 🏗️ **Production Ready**: Robust error handling and validation
- 🔍 **Comprehensive**: Full coverage of TZDB files and formats
- 📊 **Multiple Outputs**: JSON, dictionaries, pandas DataFrames
- 🌍 **Geographic Data**: Timezone coordinates and country mappings
- ⏰ **Transition Analysis**: DST and offset change calculations

## Installation

```bash
pip install x-zic
```

Or clone from source:
```bash
git clone https://github.com/mlotfic/x-zic
cd x-zic
pip install -e .
```

## Quick Start

```python
from x_zic import read_zones, get_transitions

# Read all timezones (automatically caches for future calls)
zones = read_zones()
print(f"Found {len(zones)} timezones")

# Get DST transitions for New York
transitions = get_transitions('America/New_York', 2020, 2025)
for transition in transitions[:3]:  # Show first 3
    print(f"{transition['timestamp']}: {transition['abbrev']} ({transition['offset_after']})")
```

## Basic Usage

### Reading Timezone Data

```python
import x_zic

# Read all zones
all_zones = x_zic.read_zones()

# Read by region
european_zones = x_zic.read_zones('europe')
asian_zones = x_zic.read_zones('asia')

# Parse specific files
from x_zic.parser import parse_zone, parse_rule
zones = parse_zone('northamerica', loader)
rules = parse_rule('europe', loader)
```

### Working with Transitions

```python
# Get DST transitions
transitions = x_zic.get_transitions(
    'America/Los_Angeles', 
    start_year=2020, 
    end_year=2025
)

# Analyze transition patterns
for t in transitions:
    print(f"{t['timestamp']} | {t['abbrev']:>4} | "
          f"{t['offset_before']} → {t['offset_after']} | "
          f"DST: {t['is_dst']}")
```

### Geographic Data

```python
from x_zic.geo import read_zonetab

# Get timezones with coordinates
geo_zones = read_zonetab()
for zone in geo_zones[:5]:
    print(f"{zone['zone_id']} | {zone['country_code']} | "
          f"({zone['latitude']}, {zone['longitude']})")
```

## Advanced Usage

### Custom Configuration

```python
from x_zic.core.config import TZDBConfig
from x_zic.core.loader import FileLoader

# Custom setup
config = TZDBConfig(
    tzdb_source_path="/path/to/tzdb-2025b",
    cache_dir="/tmp/tzdb_cache",
    max_transition_years=50
)

loader = FileLoader(config)
```

### Low-level Parsing

```python
from x_zic.parser import parse_zone_line, parse_rule_line

# Parse individual lines
zone_line = "Zone America/New_York -5:00 US E%sT"
zone = parse_zone_line(zone_line)

rule_line = "Rule US 2007 max - Mar Sun>=8 2:00 1:00 D"
rule = parse_rule_line(rule_line)
```

### Analysis and Export

```python
from x_zic.analysis import stats
from x_zic.export import to_dataframe

# Get statistics
zone_stats = stats.count_zones_by_region()
dst_stats = stats.dst_coverage(2024)

# Export to pandas
df_zones = to_dataframe(read_zones())
df_rules = to_dataframe(read_rules())

print(f"Zones per region: {zone_stats}")
print(f"DST coverage: {dst_stats['percentage']:.1f}%")
```

## API Reference

### Core Functions

| Function | Description |
|----------|-------------|
| `read_zones(region=None)` | Read all zones or specific region |
| `get_transitions(zone_name, start_year, end_year)` | Get DST/offset transitions |
| `parse_zone_file(filename)` | Parse specific zone file |

### Parser Module

| Function | Description |
|----------|-------------|
| `parse_zone(file, loader)` | Parse zone file to objects |
| `parse_rule(file, loader)` | Parse rule file to objects |
| `parse_link(file, loader)` | Parse link file to objects |
| `parse_leap(file, loader)` | Parse leap seconds file |

### Regions Module

| Function | Description |
|----------|-------------|
| `list_regions()` | Get available region names |
| `get_zones_by_region(region, loader)` | Get zones from region |
| `get_rules_by_region(region, loader)` | Get rules from region |

## Data Models

### Zone
```python
{
    'name': 'America/New_York',
    'offset': '-5:00', 
    'rules': 'US',
    'format': 'E%sT',
    'until': None,
    'region': 'northamerica'
}
```

### Rule  
```python
{
    'name': 'US',
    'from_year': 2007,
    'to_year': 'max',
    'month': 'Mar',
    'day': 'Sun>=8',
    'time': '2:00',
    'save': '1:00',
    'letter': 'D'
}
```

### Transition
```python
{
    'zone': 'America/New_York',
    'timestamp': '2024-03-10T07:00:00',
    'offset_before': '-05:00',
    'offset_after': '-04:00', 
    'is_dst': True,
    'abbrev': 'EDT'
}
```

## Cache System

The library automatically caches parsed data for instant subsequent loads:

```
.tzdb_cache/
├── zones.json
├── rules.json
├── links.json
├── leapseconds.json
└── regions.json
```

Clear cache when needed:
```python
x_zic.clear_cache()
```

## Performance

| Operation | First Run | Cached Run |
|-----------|-----------|------------|
| Load all zones | ~500ms | ~50ms |
| Find zone by name | ~10ms | ~1ms |
| Calculate transitions | ~100ms | ~20ms |

## File Support

The parser handles all standard TZDB files:

- **Region Files**: `africa`, `asia`, `europe`, `northamerica`, etc.
- **Legacy Files**: `backward`, `backzone`  
- **Geographic Data**: `zone.tab`, `zone1970.tab`, `iso3166.tab`
- **Leap Seconds**: `leapseconds`, `leap-seconds.list`
- **Compiled Data**: `tzdata.zi`

## Examples

### Find All DST-Observing Zones
```python
zones = read_zones()
dst_zones = [
    zone for zone in zones 
    if zone['rules'] not in ['-', '', None]
]
print(f"Found {len(dst_zones)} DST-observing zones")
```

### Calculate Offset Changes
```python
transitions = get_transitions('Europe/London', 2023, 2024)
for t in transitions:
    change = "DST Start" if t['is_dst'] else "DST End"
    print(f"{t['timestamp'][:10]}: {change} ({t['abbrev']})")
```

### Geographic Queries
```python
from x_zic.geo import read_zonetab

geo_zones = read_zonetab()
us_zones = [z for z in geo_zones if z['country_code'] == 'US']

for zone in us_zones:
    print(f"{zone['zone_id']} - {zone['comments']}")
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=x_zic tests/

# Specific test module
python -m pytest tests/test_parser.py -v
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- IANA Time Zone Database for maintaining the official timezone data
- Python datetime and zoneinfo modules for inspiration
- Contributors and users of the library

## Support

- 📚 [Documentation](https://github.com/mlotfic/x-zic/docs)
- 🐛 [Issue Tracker](https://github.com/mlotfic/x-zic/issues)
- 💬 [Discussions](https://github.com/mlotfic/x-zic/discussions)

---

**Ready to parse timezones?** Install the library and start with the [Quick Start](#quick-start) guide!