from x_zic import read_zones, get_transitions

# Read all zones (uses cache automatically)
zones = read_zones()
print(f"Found {len(zones)} zones")

# Read zones from specific region
europe_zones = read_zones('europe')
print(f"Found {len(europe_zones)} European zones")

# Get transitions for a zone
transitions = get_transitions('America/New_York', 2020, 2025)
for transition in transitions:
    print(f"{transition['timestamp']}: {transition['abbrev']} ({transition['offset_after']})")