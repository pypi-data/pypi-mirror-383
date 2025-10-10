from x_zic.core.loader import FileLoader
from x_zic.core.config import TZDBConfig
from x_zic.parser import parse_zone, parse_rule

# Custom configuration
config = TZDBConfig(
    tzdb_source_path="/path/to/tzdb-2025b",
    cache_dir="/tmp/tzdb_cache"
)

loader = FileLoader(config)

# Parse specific files
zones = parse_zone('europe', loader)
rules = parse_rule('europe', loader)

print(f"Parsed {len(zones)} zones and {len(rules)} rules from Europe")

# Clear cache if needed
loader.clear_cache()