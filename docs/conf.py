import sys
import os
import pathlib as pl
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.append(os.path.join(str(list(pl.Path(__file__).parents)[1]), "modules", "integration"))
sys.path.append(os.path.join(str(list(pl.Path(__file__).parents)[1]), "modules", "MCS"))

project = 'RBDO UAM'
copyright = '2023, Damien'
author = 'Damien'
release = '0.0.0'



extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
source_suffix = ['.rst']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
