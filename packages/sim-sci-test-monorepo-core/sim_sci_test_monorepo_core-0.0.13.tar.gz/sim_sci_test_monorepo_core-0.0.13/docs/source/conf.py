#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Sim Science Test Monorepo Core documentation build configuration file

import sys
from pathlib import Path

# Add the package to the Python path
sys.path.insert(0, str(Path("../../src").resolve()))

# Import the package to get version info
import sim_sci_test_monorepo.core

# -- Project information -----------------------------------------------------

project = "Sim Science Test Monorepo - Core"
copyright = "2025, IHME"
author = "IHME"

# The short X.Y version and full version
try:
    from sim_sci_test_monorepo.core._version import version
    release = version
    version = version
except ImportError:
    # Fallback if version file doesn't exist
    version = "0.1.0"
    release = "0.1.0"

# -- General configuration ------------------------------------------------

needs_sphinx = "4.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints", 
    "sphinx.ext.intersphinx",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = []
pygments_style = "sphinx"
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_sidebars = {
    "**": [
        "globaltoc.html",
        "searchbox.html",
    ]
}

# -- Options for HTMLHelp output ------------------------------------------

htmlhelp_basename = "sim-sci-test-monorepo-core-doc"

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

latex_documents = [
    (
        master_doc,
        "sim-sci-test-monorepo-core.tex",
        "Sim Science Test Monorepo Core Documentation",
        "IHME",
        "manual",
    ),
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    (
        master_doc, 
        "sim-sci-test-monorepo-core", 
        "Sim Science Test Monorepo Core Documentation", 
        [author], 
        1
    )
]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (
        master_doc,
        "sim-sci-test-monorepo-core",
        "Sim Science Test Monorepo Core Documentation",
        author,
        "sim-sci-test-monorepo-core",
        "Core functionality for sim_sci_test_monorepo",
        "Miscellaneous",
    ),
]

# Other docs we can link to
intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# -- Autodoc configuration ------------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource", 
    "undoc-members": True,
    "private-members": False,
}

autodoc_typehints = "description"

# -- nitpicky mode --------------------------------------------------------

nitpicky = True
nitpick_ignore = []