Getting Started
===============

Installation
------------

Basic Installation
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    pip install x-zic

With Optional Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # For pandas integration
    pip install x-zic[pandas]

    # For analysis features
    pip install x-zic[analysis]

    # For development
    pip install x-zic[dev]

Basic Usage
-----------

Reading Timezone Data
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import x_zic

    # Read all zones
    all_zones = x_zic.read_zones()
    print(f"Found {len(all_zones)} timezones")

    # Read by region
    european_zones = x_zic.read_zones('europe')
    asian_zones = x_zic.read_zones('asia')

Working with Transitions
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Get DST transitions
    transitions = x_zic.get_transitions(
        'America/Los_Angeles', 
        start_year=2020, 
        end_year=2025
    )

    # Analyze transition patterns
    for t in transitions:
        print(f"{t['timestamp']} | {t['abbrev']:>4} | "
              f"{t['offset_before']} → {t['offset_after']}")

Geographic Data
^^^^^^^^^^^^^^^

.. code-block:: python

    from x_zic.geo import read_zonetab

    # Get timezones with coordinates
    geo_zones = read_zonetab()
    for zone in geo_zones[:5]:
        print(f"{zone['zone_id']} | {zone['country_code']} | "
              f"({zone['latitude']}, {zone['longitude']})")

Core Concepts
-------------

Time Zone Database
^^^^^^^^^^^^^^^^^^

The IANA Time Zone Database (TZDB) is the authoritative source for timezone information worldwide. It contains:

* **Zone definitions**: Timezone rules and offsets
* **Rule sets**: DST transition rules
* **Links**: Aliases and deprecated names
* **Geographic data**: Coordinates and country codes

x-zic provides a complete parser for all TZDB components.

Caching System
^^^^^^^^^^^^^^

x-zic automatically caches parsed data for optimal performance:

* **First run**: Parses TZDB files and creates cache
* **Subsequent runs**: Loads from cache instantly
* **Cache validation**: Automatically detects source changes
* **Manual control**: Clear cache when needed

.. code-block:: python

    # Clear cache manually
    x_zic.clear_cache()

Data Models
^^^^^^^^^^^

The library uses simple, serializable data models:

.. code-block:: python

    # Zone example
    {
        'name': 'America/New_York',
        'offset': '-5:00', 
        'rules': 'US',
        'format': 'E%sT',
        'region': 'northamerica'
    }

    # Transition example  
    {
        'zone': 'America/New_York',
        'timestamp': '2024-03-10T07:00:00',
        'offset_before': '-05:00',
        'offset_after': '-04:00', 
        'is_dst': True,
        'abbrev': 'EDT'
    }

Next Steps
----------

Ready for more? Check out:

* :doc:`advanced-usage` for custom configurations and performance tuning
* :doc:`examples` for practical use cases and recipes
* :doc:`api-reference` for complete API documentation