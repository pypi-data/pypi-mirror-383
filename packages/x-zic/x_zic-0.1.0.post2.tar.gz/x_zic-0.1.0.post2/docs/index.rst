x-zic: High-performance TZDB Parser
====================================

.. image:: https://img.shields.io/pypi/v/x-zic.svg
    :target: https://pypi.org/project/x-zic/
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/x-zic.svg
    :target: https://pypi.org/project/x-zic/
    :alt: Python Versions

.. image:: https://readthedocs.org/projects/x-zic/badge/?version=latest
    :target: https://x-zic.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://github.com/your-username/x-zic/blob/main/LICENSE
    :alt: License

A high-performance Python library for parsing and analyzing the IANA Time Zone Database (tzdb). Built for production use with smart caching, minimal dependencies, and a practical API.

.. rubric:: Features

* 🚀 **Blazing Fast**: Smart caching system for instant subsequent loads
* 📦 **Zero Dependencies**: Pure Python standard library
* 🏗️ **Production Ready**: Robust error handling and validation
* 🔍 **Comprehensive**: Full coverage of TZDB files and formats
* 📊 **Multiple Outputs**: JSON, dictionaries, pandas DataFrames
* 🌍 **Geographic Data**: Timezone coordinates and country mappings
* ⏰ **Transition Analysis**: DST and offset change calculations

Quick Start
-----------

.. code-block:: python

    from x_zic import read_zones, get_transitions

    # Read all timezones (automatically caches for future calls)
    zones = read_zones()
    print(f"Found {len(zones)} timezones")

    # Get DST transitions for New York
    transitions = get_transitions('America/New_York', 2020, 2025)
    for transition in transitions[:3]:
        print(f"{transition['timestamp']}: {transition['abbrev']}")

Installation
------------

.. code-block:: bash

    pip install x-zic

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting-started
   advanced-usage
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api-reference

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`