# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../acat'))
sys.path.insert(0, os.path.abspath('../acat/build'))
sys.path.insert(0, os.path.abspath('../acat/ga'))


# -- Project information -----------------------------------------------------

project = 'ACAT'
copyright = '2021, Shuang Han'
author = 'Shuang Han'

# The full version, including alpha/beta/rc tags
release = '1.7.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
napoleon_use_param = True
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.doctest',
              'sphinx.ext.todo',
              'sphinx.ext.coverage',
              'sphinx.ext.mathjax',
              'sphinx.ext.ifconfig',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode',
              'sphinx.ext.autosummary',
              'sphinx.ext.napoleon',
              'sphinx.ext.graphviz',
              #'sphinx_autodoc_typehints',
              'sphinx_sitemap',
              'cloud_sptheme.ext.table_styling']

autodoc_member_order = 'bysource'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_favicon = 'acat_favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

#latex_documents = [
# ('index', 'acat.tex', u'ACAT', u'Shuang Han', 'manual'),
#]
