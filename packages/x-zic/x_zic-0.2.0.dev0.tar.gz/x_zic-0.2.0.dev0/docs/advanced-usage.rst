Advanced Usage
==============

Custom Configuration
--------------------

.. code-block:: python

    from x_zic.core.config import TZDBConfig
    from x_zic.core.loader import FileLoader

    # Custom setup
    config = TZDBConfig(
        tzdb_source_path="/path/to/tzdb-2025b",
        cache_dir="/tmp/tzdb_cache",
        max_transition_years=50
    )

    loader = FileLoader(config)

Configuration Options
^^^^^^^^^^^^^^^^^^^^^

.. list-table:: TZDBConfig Options
   :header-rows: 1

   * - Option
     - Type
     - Default
     - Description
   * - tzdb_source_path
     - str
     - "tzdb-2025b"
     - Path to TZDB source files
   * - cache_dir
     - str
     - ".tzdb_cache"
     - Cache directory
   * - cache_enabled
     - bool
     - True
     - Enable caching
   * - max_transition_years
     - int
     - 100
     - Max years for transition calculations

Low-level Parsing
-----------------

.. code-block:: python

    from x_zic.parser import parse_zone_line, parse_rule_line

    # Parse individual lines
    zone_line = "Zone America/New_York -5:00 US E%sT"
    zone = parse_zone_line(zone_line)

    rule_line = "Rule US 2007 max - Mar Sun>=8 2:00 1:00 D"
    rule = parse_rule_line(rule_line)

File Loader Direct Usage
------------------------

.. code-block:: python

    from x_zic.core.loader import FileLoader
    from x_zic.core.config import TZDBConfig

    config = TZDBConfig()
    loader = FileLoader(config)

    # Load specific files
    lines = loader.load_file('europe')
    zones = parse_zone('europe', loader)
    rules = parse_rule('europe', loader)

Performance Tuning
------------------

Cache Optimization
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Disable cache for one-time parsing
    loader.load_file('europe', use_cache=False)

    # Pre-warm cache for common regions
    for region in ['europe', 'northamerica', 'asia']:
        x_zic.read_zones(region)

Memory Management
^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Clear memory cache
    loader = FileLoader(config)
    # Memory cache is automatically managed

    # Clear disk cache
    loader.clear_cache()

Error Handling
--------------

File Not Found
^^^^^^^^^^^^^^

.. code-block:: python

    from x_zic.core.loader import FileLoader

    loader = FileLoader(config)
    
    try:
        zones = parse_zone('nonexistent', loader)
    except FileNotFoundError as e:
        print(f"File not found: {e}")

Invalid Data
^^^^^^^^^^^^

.. code-block:: python

    from x_zic.parser import parse_zone_line

    try:
        zone = parse_zone_line("Invalid line")
        if zone is None:
            print("Line is not a valid zone definition")
    except Exception as e:
        print(f"Parse error: {e}")

Integration Patterns
--------------------

With Pandas
^^^^^^^^^^^

.. code-block:: python

    import pandas as pd
    from x_zic import read_zones

    # Convert to DataFrame
    zones = read_zones()
    df_zones = pd.DataFrame(zones)
    
    # Analyze zone distribution
    zone_counts = df_zones['region'].value_counts()
    print(zone_counts)

With Database
^^^^^^^^^^^^^

.. code-block:: python

    import sqlite3
    import json
    from x_zic import read_zones, get_transitions

    # Store zones in SQLite
    zones = read_zones()
    conn = sqlite3.connect('timezones.db')
    
    # Create table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            name TEXT PRIMARY KEY,
            offset TEXT,
            rules TEXT,
            format TEXT,
            region TEXT
        )
    ''')
    
    # Insert data
    for zone in zones:
        conn.execute(
            'INSERT OR REPLACE INTO zones VALUES (?, ?, ?, ?, ?)',
            (zone['name'], zone['offset'], zone['rules'], 
             zone['format'], zone['region'])
        )
    
    conn.commit()

Custom Cache Backends
---------------------

You can implement custom cache backends by extending the FileLoader class:

.. code-block:: python

    from x_zic.core.loader import FileLoader
    import redis

    class RedisCacheLoader(FileLoader):
        def __init__(self, config, redis_client):
            super().__init__(config)
            self.redis = redis_client
        
        def _load_from_cache(self, filename):
            cache_key = f"tzdb:{self._get_cache_key(filename)}"
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
            return None
        
        def _save_to_cache(self, filename, data):
            cache_key = f"tzdb:{self._get_cache_key(filename)}"
            self.redis.setex(cache_key, 3600, json.dumps(data))

Best Practices
--------------

1. **Use caching in production**: Enable caching for best performance
2. **Handle file errors**: Always wrap file operations in try/except
3. **Validate inputs**: Check zone names and year ranges
4. **Monitor cache size**: Clear cache periodically if disk space is limited
5. **Use region filtering**: Load only needed regions to reduce memory usage