# docs/source/conf.py
import os
import sys

# 1. Path setup: Points Sphinx directly to your /src directory for autodoc
sys.path.insert(0, os.path.abspath('../../src'))

# 2. Project information
project = 'Lichess-MakeChessBetter'
author = 'Aarav Patel'
copyright = '2026, Aarav Patel'
release = '2.0.0'

# 3. General configuration
# Includes extensions for auto-generating docs from docstrings and reading Markdown
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # Supports Google/NumPy style docstrings
    'myst_parser'           # Allows you to use Markdown (.md) files for docs instead of just RestructuredText (.rst)
]

templates_path = ['_templates']
exclude_patterns = []

# 4. Mock heavy/compiled external modules that can't run on Read the Docs
# Add any libraries here that might crash the build if they try to import local binaries
autodoc_mock_imports = ["chess"] 

# 5. Options for HTML output
html_theme = 'sphinx_rtd_theme'  # Standard, beautiful Read the Docs look
html_static_path = ['_static']
