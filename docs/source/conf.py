# pylint: disable=invalid-name

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../../'))

project = 'hgpmatch'
copyright = '2020, Kelly Littlepage' # pylint: disable=redefined-builtin
author = 'Kelly Littlepage <kelly@klittlepage.com>'

release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme'
]

napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True

master_doc = 'index'
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
