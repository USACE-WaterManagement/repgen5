import os, sys
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../repgen'))
sys.path.insert(0, os.path.abspath('../../tests'))
from repgen.__main__ import version

project = 'USACE WM Repgen5'
copyright = '2024, HEC,MISC'
author = 'HEC,MISC'
release = version
extensions = [
    'myst_parser',             
    'sphinx_copybutton',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode'
]
source_suffix = {'.md': 'markdown', '.rst': 'restructuredtext'}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

master_doc = 'index'
language = 'en'

html_theme = 'alabaster'
html_static_path = ['_static', '_static/css', '_static/js']
html_css_files = [
    'css/custom.css',
]
html_js_files = [
    'js/custom.js',
]

man_pages = [
    (master_doc, 'Repgen5', 'Repgen5 Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'Repgen5', 'Repgen5 Name Documentation',
     author, 'Repgen5', 'A program for creating simple fixed format text reports using the CWMS Data API.',
     'Miscellaneous'),
]

autodoc_member_order = 'bysource'

todo_include_todos = True

myst_enable_extensions = [
    "colon_fence",  
]
