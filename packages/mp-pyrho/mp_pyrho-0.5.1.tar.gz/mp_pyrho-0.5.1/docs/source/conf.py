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

sys.path.insert(0, os.path.abspath("../.."))


# -- Project information -----------------------------------------------------

project = "mp-pyrho"
copyright = "2022, Materials Project Team"
author = "Jimmy-Xuan Shen"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "m2r2",
    "nbsphinx",
    "nbsphinx_link",
    "autoapi.extension",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["Thumbs.db", ".DS_Store", "test*.py"]

# use type hints
autoapi_dirs = ["../../src"]
autoapi_add_toctree_entry = False
autoapi_python_class_content = "class"
# autoapi_options = ["members", "show-module-summary", "show-inheritance"]
autoapi_options = [
    "members",
    "private-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
# autodoc_typehints = "description"
# autoclass_content = 'init'

# better napoleon support
# napoleon_use_param = True
# napoleon_use_rtype = True
# napoleon_use_ivar = True
napoleon_numpy_docstring = True

# The suffix(es) of source filenames.
source_suffix = [".rst", ".md"]

# Ensure env.metadata[env.docname]['nbsphinx-link-target'] points relative to repo root:
nbsphinx_link_target_root = os.path.join(__file__, "..", "..")

nbsphinx_prolog = r"""
{% if env.metadata[env.docname]['nbsphinx-link-target'] %}
{% set docpath = env.metadata[env.docname]['nbsphinx-link-target'] %}
{% else %}
{% set docpath = env.doc2path(env.docname, base='docs/source/') %}
{% endif %}
.. only:: html
    .. role:: raw-html(raw)
        :format: html
    .. nbinfo::
        This page is available as a Jupyter notebook: `{{ docpath }}`__.
    __ https://github.com/materialsproject/jobflow/tree/main/{{ docpath }}"""


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# hide sphinx footer
html_show_sphinx = False
html_show_sourcelink = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
fonts = [
    "Lato",
    "-apple-system",
    "BlinkMacSystemFont",
    "Segoe UI",
    "Helvetica",
    "Arial",
    "sans-serif",
    "Apple Color Emoji",
    "Segoe UI Emoji",
]
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "light_css_variables": {
        "admonition-font-size": "92%",
        "admonition-title-font-size": "92%",
        "font-stack": ",".join(fonts),
        "font-size--small": "92%",
        "font-size--small--2": "87.5%",
        "font-size--small--3": "87.5%",
        "font-size--small--4": "87.5%",
    },
    "dark_css_variables": {
        "admonition-font-size": "92%",
        "admonition-title-font-size": "92%",
        "font-stack": ",".join(fonts),
        "font-size--small": "92%",
        "font-size--small--2": "87.5%",
        "font-size--small--3": "87.5%",
        "font-size--small--4": "87.5%",
    },
}
html_title = "pyRho"
