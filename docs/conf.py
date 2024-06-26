# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
# autodoc_member_order = 'bysource'  # uncomment to not have alphabetical list.

sys.path.append(os.path.abspath('./content/'))
sys.path.append(os.path.abspath('../../../../../'))
sys.path.append(os.path.abspath('../../../../'))
sys.path.append(os.path.abspath('../../../'))
sys.path.append(os.path.abspath('../../'))

# -- Project information -----------------------------------------------------

project = 'SIMIO-continuum'
copyright = '2022, Nicolas Kurtovic'
author = 'Nicolas Kurtovic'

# The full version, including alpha/beta/rc tags
release = '1.2'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx.ext.imgmath',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
    'nbsphinx', 
]

#html_theme = 'sphinx_rtd_theme'
#latex_engine = 'pdflatex'
#imgmath_latex = "pdflatex"
#imgmath_image_format = 'png'

# Mathjax path
mathjax_path = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'
#mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS-MML_HTMLorMML'

# astropy
autodoc_mock_imports = ['astropy']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Make sure the functions are in the order in the .py file.
add_function_parentheses = True

# -- Options for HTML output -------------------------------------------------

# Readthedocs.
on_rtd = os.environ.get("READTHEDOCS", None) == "True"
if not on_rtd:
    import sphinx_rtd_theme
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
#html_favicon = "_static/favicon.png"
html_logo = "_static/SIMIO_logo.png"
html_theme_options = {"logo_only": True}
