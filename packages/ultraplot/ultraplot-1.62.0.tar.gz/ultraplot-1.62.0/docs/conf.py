# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# For autodoc compilation see:
# https://medium.com/@eikonomega/getting-started-with-sphinx-autodoc-part-1-2cebbbca5365
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Imports and paths --------------------------------------------------------------

# Import statements
import os
import sys
import datetime
import subprocess
from pathlib import Path

# Surpress warnings from cartopy when downloading data inside docs env
import warnings

try:
    from cartopy.io import DownloadWarning

    warnings.filterwarnings("ignore", category=DownloadWarning)
except ImportError:
    # In case cartopy isn't installed yet when conf.py is executed
    pass

# Handle sphinx.util.console deprecation
# Note this has been deprecated in Sphinx 5.0 and some extensions still use the console module. Needs to be updated later
try:
    # For newer Sphinx versions where sphinx.util.console is removed
    import sphinx

    if not hasattr(sphinx.util, "console"):
        # Create a compatibility layer
        import sys
        import sphinx.util
        from sphinx.util import logging

        class ConsoleColorFallback:
            def __getattr__(self, name):
                return (
                    lambda text: text
                )  # Return a function that returns the text unchanged

        sphinx.util.console = ConsoleColorFallback()
except Exception:
    pass

# Build what's news page from github releases
from subprocess import run

run("python _scripts/fetch_releases.py".split(), check=False)

# Update path for sphinx-automodapi and sphinxext extension
sys.path.append(os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

# Print available system fonts
from matplotlib.font_manager import fontManager


# -- Project information -------------------------------------------------------
# The basic info
project = "UltraPlot"
copyright = f"{datetime.datetime.today().year}, UltraPlot"
author = "Luke L. B. Davis"

# The short X.Y version
version = ""

# The full version, including alpha/beta/rc tags
release = ""

# Faster builds
parallel_read_safe = True
parallel_write_safe = True

# -- Create files --------------------------------------------------------------

# Create RST table and sample ultraplotrc file
from ultraplot.config import rc

folder = (Path(__file__).parent / "_static").absolute()
if not folder.is_dir():
    folder.mkdir()

rc._save_rst(str(folder / "rctable.rst"))
rc._save_yaml(str(folder / "ultraplotrc"))

# -- Setup basemap --------------------------------------------------------------

# Hack to get basemap to work
# See: https://github.com/readthedocs/readthedocs.org/issues/5339
if os.environ.get("READTHEDOCS", None) == "True":
    conda = (
        Path(os.environ["CONDA_ENVS_PATH"]) / os.environ["CONDA_DEFAULT_ENV"]
    ).absolute()
else:
    conda = Path(os.environ["CONDA_PREFIX"]).absolute()
os.environ["GEOS_DIR"] = str(conda)
os.environ["PROJ_LIB"] = str((conda / "share" / "proj"))

# Install basemap if does not exist
# Extremely ugly but impossible to install in environment.yml. Must set
# GEOS_DIR before installing so cannot install with pip and basemap conflicts
# with conda > 0.19 so cannot install with conda in environment.yml.
try:
    import mpl_toolkits.basemap  # noqa: F401
except ImportError:
    subprocess.check_call(
        ["pip", "install", "basemap"]
        # ["pip", "install", "git+https://github.com/matplotlib/basemap@v1.2.2rel"]
    )


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "matplotlib.sphinxext.plot_directive",  # see: https://matplotlib.org/sampledoc/extensions.html  # noqa: E501
    "sphinx.ext.autodoc",  # include documentation from docstrings
    "sphinx_design",
    "sphinx.ext.doctest",  # >>> examples
    "sphinx.ext.extlinks",  # for :pr:, :issue:, :commit:
    "sphinx.ext.autosectionlabel",  # use :ref:`Heading` for any heading
    "sphinx.ext.todo",  # Todo headers and todo:: directives
    "sphinx.ext.mathjax",  # LaTeX style math
    "sphinx.ext.viewcode",  # view code links
    "sphinx.ext.napoleon",  # for NumPy style docstrings
    "sphinx.ext.intersphinx",  # external links
    "sphinx.ext.autosummary",  # autosummary directive
    "sphinxext.custom_roles",  # local extension
    "sphinx_automodapi.automodapi",  # fork of automodapi
    "sphinx_rtd_light_dark",  # use custom theme
    "sphinx_copybutton",  # add copy button to code
    "_ext.notoc",
    "nbsphinx",  # parse rst books
]


# The master toctree document.
master_doc = "index"

# The suffix(es) of source filenames, either a string or list.
source_suffix = [".rst", ".html"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of file patterns relative to source dir that should be ignored
exclude_patterns = [
    "conf.py",
    "sphinxext",
    "_build",
    "_scripts",
    "_templates",
    "_themes",
    "*.ipynb",
    "**.ipynb_checkpoints" ".DS_Store",
    "trash",
    "tmp",
]

autodoc_default_options = {
    "private-members": False,
    "special-members": False,
    "undoc-members": False,
}

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = "en"

# Role. Default family is py but can also set default role so don't need
# :func:`name`, :module:`name`, etc.
default_role = "py:obj"

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False  # UltraPlot imports everything in top-level namespace

# Autodoc configuration. Here we concatenate class and __init__ docstrings
# See: http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autoclass_content = "both"  # options are 'class', 'both', 'init'

# Generate stub pages whenever ::autosummary directive encountered
# This way don't have to call sphinx-autogen manually
autosummary_generate = True

# Automodapi tool: https://sphinx-automodapi.readthedocs.io/en/latest/automodapi.html
# Normally have to *enumerate* function names manually. This will document them
# automatically. Just be careful to exclude public names from automodapi:: directive.
automodapi_toctreedirnm = "api"
automodsumm_inherited_members = False

# Doctest configuration. For now do not run tests, they are just to show syntax
# and expected output may be graphical
doctest_test_doctest_blocks = ""

# Cupybutton configuration
# See: https://sphinx-copybutton.readthedocs.io/en/latest/
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True
copybutton_remove_prompts = True

# Links for What's New github commits, issues, and pull requests
extlinks = {
    "issue": ("https://github.com/ultraplot/ultraplot/issues/%s", "GH#%s"),
    "commit": ("https://github.com/Ultraplot/ultraplot/commit/%s", "@%s"),
    "pr": ("https://github.com/Ultraplot/ultraplot/pull/%s", "GH#%s"),
}

# Set up mapping for other projects' docs
intersphinx_mapping = {
    "cycler": ("https://matplotlib.org/cycler/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
    "cartopy": ("https://cartopy.readthedocs.io/stable/", None),
    "basemap": ("https://matplotlib.org/basemap/stable/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "pint": ("https://pint.readthedocs.io/en/stable/", None),
    "networkx": ("https://networkx.org/documentation/stable/", None),
}


# Fix duplicate class member documentation from autosummary + numpydoc
# See: https://github.com/phn/pytpm/issues/3#issuecomment-12133978
numpydoc_show_class_members = False

# Napoleon options
# See: http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
# * use_param is set to False so that we can put multiple "parameters"
#   on one line -- for example 'xlocator, ylocator : locator-spec, optional'
# * docs claim napoleon_preprocess_types and napoleon_type_aliases only work
#   when napoleon_use_param is True but xarray sets to False and it still works
# * use_keyword is set to False because we do not want separate 'Keyword Arguments'
#   section and have same issue for multiple keywords.
# * use_ivar and use_rtype are set to False for (presumably) style consistency
#   with the above options set to False.
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_keyword = False
napoleon_use_rtype = False
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_include_init_with_doc = False  # move init doc to 'class' doc
napoleon_preprocess_types = True
napoleon_type_aliases = {
    # Python or inherited terms
    # NOTE: built-in types are automatically included
    "callable": ":py:func:`callable`",
    "sequence": ":term:`sequence`",
    "dict-like": ":term:`dict-like <mapping>`",
    "path-like": ":term:`path-like <path-like object>`",
    "array-like": ":term:`array-like <array_like>`",
    # UltraPlot defined terms
    "unit-spec": ":py:func:`unit-spec <ultraplot.utils.units>`",
    "locator-spec": ":py:func:`locator-spec <ultraplot.constructor.Locator>`",
    "formatter-spec": ":py:func:`formatter-spec <ultraplot.constructor.Formatter>`",
    "scale-spec": ":py:func:`scale-spec <ultraplot.constructor.Scale>`",
    "colormap-spec": ":py:func:`colormap-spec <ultraplot.constructor.Colormap>`",
    "cycle-spec": ":py:func:`cycle-spec <ultraplot.constructor.Cycle>`",
    "norm-spec": ":py:func:`norm-spec <ultraplot.constructor.Norm>`",
    "color-spec": ":py:func:`color-spec <matplotlib.colors.is_color_like>`",
    "artist": ":py:func:`artist <matplotlib.artist.Artist>`",
}

# Fail on error. Note nbsphinx compiles all notebooks in docs unless excluded
nbsphinx_allow_errors = False

# Give *lots* of time for cell execution
nbsphinx_timeout = 300

# Add jupytext support to nbsphinx
nbsphinx_custom_formats = {".py": ["jupytext.reads", {"fmt": "py:percent"}]}

nbsphinx_execute = "auto"

# The name of the Pygments (syntax highlighting) style to use.
# The light-dark theme toggler overloads this, but set default anyway
pygments_style = "none"


# -- Options for HTML output -------------------------------------------------

# Logo
html_logo = str(Path("_static") / "logo_square.png")

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# Use modified RTD theme with overrides in custom.css and custom.js
style = None
html_theme = "sphinx_rtd_light_dark"
# html_theme = "alabaster"
# html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": True,
    "display_version": False,
    "collapse_navigation": True,
    "navigation_depth": 4,
    "prev_next_buttons_location": "bottom",  # top and bottom
    "includehidden": True,
    "titles_only": True,
    "display_toc": True,
    "sticky_navigation": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
# html_sidebars = {}

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large. Static folder is for CSS and image files. Use ImageMagick to
# convert png to ico on command line with 'convert image.png image.ico'
html_favicon = str(Path("_static") / "logo_blank.svg")

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "ultraplotdoc"


html_css_files = [
    "custom.css",
]
html_js_files = [
    "custom.js",
]

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
    # Latex figure (float) alignment
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "UltraPlot.tex", "UltraPlot Documentation", "UltraPlot", "manual"),
]

primary_domain = "py"

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "UltraPlot", "UltraPlot Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "UltraPlot",
        "UltraPlot Documentation",
        author,
        "UltraPlot",
        "A succinct matplotlib wrapper for making beautiful, "
        "publication-quality graphics.",
        "Miscellaneous",
    )
]


# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

from ultraplot.internals.docstring import _snippet_manager


def process_docstring(app, what, name, obj, options, lines):
    if lines:
        try:
            # Create a proper format string
            doc = "\n".join(lines)
            expanded = doc % _snippet_manager  # Use dict directly
            lines[:] = expanded.split("\n")
        except Exception as e:
            print(f"Warning: Could not expand docstring for {name}: {e}")
            # Keep original lines if expansion fails
            pass


def setup(app):
    app.connect("autodoc-process-docstring", process_docstring)
