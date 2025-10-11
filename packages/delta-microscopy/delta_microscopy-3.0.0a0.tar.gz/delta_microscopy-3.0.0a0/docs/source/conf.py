"""Configuration file for the Sphinx documentation builder."""

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

# We import delta here because for some
# reason it fails on readthedocs if we let
# autosummary / autodoc try to load it
# themselves

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------


# -- Project information -----------------------------------------------------

project = "DeLTA"
copyright = "The DeLTA authors and contributors."
author = "Virgile Andreani, Owen O'Connor, Jean-Baptiste Lugagne, Mary Dunlop"

# The full version, including alpha/beta/rc tags
release = "dev"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.linkcode",
    "sphinx_design",
    "numpydoc",
]
autosummary_generate = True
autosummary_ignore_module_all = False
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

autodoc_typehints = "none"

master_doc = "index"


def linkcode_resolve(domain: str, info: dict[str, str]) -> str | None:
    """Determine where to point for the source of a doc item."""
    if domain != "py":
        return None

    _modname = info["module"]
    _fullname = info["fullname"]

    filename = info["module"].replace(".", "/")
    return f"https://gitlab.com/delta-microscopy/delta/-/blob/main/{filename}.py"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

html_theme_options = {
    "source_repository": "https://gitlab.com/delta-microscopy/DeLTA",
}

html_logo = "_static/DeLTA.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

autoclass_content = "class"

# Specify for readthedocs:
master_doc = "index"
