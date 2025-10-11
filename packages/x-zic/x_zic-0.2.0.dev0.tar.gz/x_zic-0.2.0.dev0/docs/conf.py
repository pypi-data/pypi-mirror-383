# Configuration file for the Sphinx documentation builder.

import os
import sys
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'x-zic'
copyright = f'{datetime.now().year}, Your Name - GNU General Public License v3'
author = 'Your Name'

# The short X.Y version
version = '0.1'
# The full version, including alpha/beta/rc tags
release = '0.1.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx_copybutton',
    'myst_parser',
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autodoc_typehints = 'description'
autodoc_mock_imports = []

# Templates
templates_path = ['_templates']

# File patterns
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Master document
master_doc = 'index'

# Language
language = 'en'

# Exclude patterns
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML theme
html_theme = 'sphinx_rtd_theme'

# Theme options
html_theme_options = {
    'analytics_id': 'G-XXXXXXXXXX',  # Optional: Google Analytics
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Static files
html_static_path = ['_static']

# Custom CSS
html_css_files = [
    'css/custom.css',
]

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

# Todo settings
todo_include_todos = True

# Copy button settings
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True