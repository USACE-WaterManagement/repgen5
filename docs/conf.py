import os, sys
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

sys.path.insert(0, os.path.abspath('../repgen'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'USACE WM Repgen5'
copyright = '2024, HEC,MISC'
author = 'HEC,MISC'
release = '5.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Enable markdown or reStructured text source docs
extensions = [
    'sphinx.ext.autodoc',      # Include documentation from docstrings
    'sphinx.ext.napoleon',     # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',     # Add links to highlighted source code
    'sphinx.ext.todo',         # Support for todo items
    'myst_parser',             # Markdown support (myst-parser)
]
source_suffix = ['.rst', '.md']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

master_doc = 'index'
language = 'en'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples.
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'Repgen5', 'Repgen5 Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples.
# (source start file, target name, title, author, dir menu entry, description, category).
texinfo_documents = [
    (master_doc, 'Repgen5', 'Repgen5 Name Documentation',
     author, 'Repgen5', 'A program for creating simple fixed format text reports using the CWMS Data API.',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------
autodoc_member_order = 'bysource'

# -- Options for napoleon extension ------------------------------------------
# napoleon_google_docstring = True
# napoleon_numpy_docstring = True

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True

# Markdown supported extensions
myst_enable_extensions = [
    "colon_fence",  # Enable ::: for block formatting
]