# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-informationalabaste

from os.path import dirname
from os.path import join
import sys



def pathdown(path, i):
    """Function to move down in levels in the given path, down meaning closer to the root path. 
    e.g. if you want to move down one level enter 1 for variable levels

    :param path: Path that needs to be altered
    :type path: string
    :param i: Amount of levels you want to move down, needs to be atleast 1
    :type i: integer
    :rtype: string
    """    
    if i < 1:
        raise Exception("Integer level must be equal or greater than 1 to avoid infinite loop")
    path_new = dirname(path)
    i = i -1
    if i == 0:
        return path_new
    else:
       return pathdown(path_new, i)

sys.path.append(pathdown(__file__, 3))
sys.path.append(join(pathdown(__file__, 3), "Flight_performance"))
sys.path.append(join(pathdown(__file__, 3), "Final_optimization"))
sys.path.append(pathdown(__file__, 1))

import structures

project = 'MDAO Wigeon'
copyright = '2022, Saullo Castro et al.'
author = 'Saullo Castro et al.'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
source_suffix = ['.rst']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
