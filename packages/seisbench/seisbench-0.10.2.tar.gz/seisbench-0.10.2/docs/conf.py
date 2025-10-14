# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from datetime import datetime

# The rename is necessary to avoid namespace collision with the version attribute for RTD
# See: https://github.com/sphinx-doc/sphinx/issues/10904
from importlib.metadata import version as _version

sys.path.insert(0, os.path.abspath("../"))
sys.path.append(os.path.abspath("_ext"))

# -- Project information -----------------------------------------------------

project = "SeisBench"
copyright = f"{datetime.now().year}, Jannes Münchmeyer, Jack Woollam"
author = "Jannes Münchmeyer, Jack Woollam"

# The full version, including alpha/beta/rc tags
release = _version("seisbench")


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx_rtd_theme",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "optional_argument_helper",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Do not add module names in the doc to hide the internal package structure of SeisBench
add_module_names = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "_static/seisbench_logo_mini.svg"
html_favicon = "_static/seisbench_favicon.svg"

html_theme_options = {
    "logo_only": True,
    "display_version": False,
}

if os.getenv("READTHEDOCS"):
    extensions.append("sphinxcontrib.googleanalytics")
    googleanalytics_id = "G-LGH5V4LJBY"
