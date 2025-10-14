# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_basics:
#
# The basics
# ==========

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_intro:
#
# Creating figures
# ----------------
#
# UltraPlot works by `subclassing
# <https://docs.python.org/3/tutorial/classes.html#inheritance>`__
# three fundamental matplotlib classes: :class:`~ultraplot.figure.Figure` replaces
# :class:`matplotlib.figure.Figure`, :class:`~ultraplot.axes.Axes` replaces :class:`matplotlib.axes.Axes`,
# and :class:`~ultraplot.gridspec.GridSpec` replaces :class:`matplotlib.gridspec.GridSpec`
# (see this `tutorial
# <https://matplotlib.org/stable/tutorials/intermediate/gridspec.html>`__
# for more on gridspecs).
#
# To make plots with these classes, you must start with the top-level commands
# :func:`~ultraplot.ui.figure`, :func:`~ultraplot.ui.subplot`, or :func:`~ultraplot.ui.subplots`. These are
# modeled after the :mod:`~matplotlib.pyplot` commands of the same name. As in
# :mod:`~matplotlib.pyplot`, :func:`~ultraplot.ui.subplot` creates a figure and a single
# subplot, :func:`~ultraplot.ui.subplots` creates a figure and a grid of subplots, and
# :func:`~ultraplot.ui.figure` creates an empty figure that can be subsequently filled
# with subplots. A minimal example with just one subplot is shown below.
#
# %% [raw] raw_mimetype="text/restructuredtext"
# .. note::
#
#    UltraPlot changes the default :rcraw:`figure.facecolor`
#    so that the figure backgrounds shown by the `matplotlib backend
#    <https://matplotlib.org/faq/usage_faq#what-is-a-backend>`__ are light gray
#    (the :rcraw:`savefig.facecolor` applied to saved figures is still white).
#    UltraPlot also controls the appearance of figures in Jupyter notebooks
#    using the new :rcraw:`inlineformat` setting, which is passed to
#    :func:`~ultraplot.config.config_inline_backend` on import. This
#    imposes a higher-quality default `"inline" format
#    <https://ipython.readthedocs.io/en/stable/interactive/plotting.html>`__
#    and disables the backend-specific settings ``InlineBackend.rc`` and
#    ``InlineBackend.print_figure_kwargs``, ensuring that the figures you save
#    look like the figures displayed by the backend.
#
#    UltraPlot also changes the default :rcraw:`savefig.format`
#    from PNG to PDF for the following reasons:
#
#        #. Vector graphic formats are infinitely scalable.
#        #. Vector graphic formats are preferred by academic journals.
#        #. Nearly all academic journals accept figures in the PDF format alongside
#           the `EPS <https://en.wikipedia.org/wiki/Encapsulated_PostScript>`__ format.
#        #. The EPS format is outdated and does not support transparent graphic
#           elements.
#
#    In case you *do* need a raster format like PNG, UltraPlot increases the
#    default :rcraw:`savefig.dpi` to 1000 dots per inch, which is
#    `recommended <https://www.pnas.org/page/authors/format>`__ by most journals
#    as the minimum resolution for figures containing lines and text. See the
#    :ref:`configuration section <ug_ultraplotrc>` for how to change these settings.
#

# %%
# Simple subplot
import numpy as np
import ultraplot as uplt

state = np.random.RandomState(51423)
data = 2 * (state.rand(100, 5) - 0.5).cumsum(axis=0)
fig, ax = uplt.subplot(suptitle="Single subplot", xlabel="x axis", ylabel="y axis")
# fig = uplt.figure(suptitle='Single subplot')  # equivalent to above
# ax = fig.subplot(xlabel='x axis', ylabel='y axis')
ax.plot(data, lw=2)


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_subplot:
#
# Creating subplots
# -----------------
#
# Similar to matplotlib, subplots can be added to figures one-by-one
# or all at once. Each subplot will be an instance of
# :class:`~ultraplot.axes.Axes`. To add subplots all at once, use
# :func:`~ultraplot.figure.Figure.add_subplots` (or its shorthand,
# :func:`~ultraplot.figure.Figure.subplots`). Note that under the hood, the top-level
# UltraPlot command :func:`~ultraplot.ui.subplots` simply calls :func:`~ultraplot.ui.figure`
# followed by :func:`~ultraplot.figure.Figure.add_subplots`.
#
# * With no arguments, :func:`~ultraplot.figure.Figure.add_subplots` returns a subplot
#   generated from a 1-row, 1-column :class:`~ultraplot.gridspec.GridSpec`.
# * With `ncols` or `nrows`, :func:`~ultraplot.figure.Figure.add_subplots` returns a
#   simple grid of subplots from a :class:`~ultraplot.gridspec.GridSpec` with
#   matching geometry in either row-major or column-major `order`.
# * With `array`, :func:`~ultraplot.figure.Figure.add_subplots` returns an arbitrarily
#   complex grid of subplots from a :class:`~ultraplot.gridspec.GridSpec` with matching
#   geometry. Here `array` is a 2D array representing a "picture" of the subplot
#   layout, where each unique integer indicates a :class:`~matplotlib.gridspec.GridSpec`
#   slot occupied by the corresponding subplot and ``0`` indicates an empty space.
#   The returned subplots are contained in a :class:`~ultraplot.gridspec.SubplotGrid`
#   (:ref:`see below <ug_subplotgrid>` for details).
#
# To add subplots one-by-one, use the :func:`~ultraplot.figure.Figure.add_subplot`
# command (or its shorthand :func:`~ultraplot.figure.Figure.subplot`).
#
# * With no arguments, :func:`~ultraplot.figure.Figure.add_subplot` returns a subplot
#   generated from a 1-row, 1-column :class:`~ultraplot.gridspec.GridSpec`.
# * With integer arguments, :func:`~ultraplot.figure.Figure.add_subplot` returns
#   a subplot matching the corresponding :class:`~ultraplot.gridspec.GridSpec` geometry,
#   as in matplotlib. Note that unlike matplotlib, the geometry must be compatible
#   with the geometry implied by previous :func:`~ultraplot.figure.Figure.add_subplot` calls.
# * With a :class:`~matplotlib.gridspec.SubplotSpec` generated by indexing a
#   :class:`~ultraplot.gridspec.GridSpec`, :func:`~ultraplot.figure.Figure.add_subplot` returns a
#   subplot at the corresponding location. Note that unlike matplotlib, only
#   one :func:`~ultraplot.figure.Figure.gridspec` can be used with each figure.
#
# As in matplotlib, to save figures, use :func:`~matplotlib.figure.Figure.savefig` (or its
# shorthand :func:`~ultraplot.figure.Figure.save`). User paths in the filename are expanded
# with :func:`~os.path.expanduser`. In the following examples, we add subplots to figures
# with a variety of methods and then save the results to the home directory.
#
# .. warning::
#
#    UltraPlot employs :ref:`automatic axis sharing <ug_share>` by default. This lets
#    subplots in the same row or column share the same axis limits, scales, ticks,
#    and labels. This is often convenient, but may be annoying for some users. To
#    keep this feature turned off, simply :ref:`change the default settings <ug_rc>`
#    with e.g. ``uplt.rc.update('subplots', share=False, span=False)``. See the
#    :ref:`axis sharing section <ug_share>` for details.

# %%
# Simple subplot grid
import numpy as np
import ultraplot as uplt

state = np.random.RandomState(51423)
data = 2 * (state.rand(100, 5) - 0.5).cumsum(axis=0)
fig = uplt.figure()
ax = fig.subplot(121)
ax.plot(data, lw=2)
ax = fig.subplot(122)
fig.format(
    suptitle="Simple subplot grid", title="Title", xlabel="x axis", ylabel="y axis"
)
# fig.save('~/example1.png')  # save the figure
# fig.savefig('~/example1.png')  # alternative


# %%
# Complex grid
import numpy as np
import ultraplot as uplt

state = np.random.RandomState(51423)
data = 2 * (state.rand(100, 5) - 0.5).cumsum(axis=0)
array = [  # the "picture" (0 == nothing, 1 == subplot A, 2 == subplot B, etc.)
    [1, 1, 2, 2],
    [0, 3, 3, 0],
]
fig = uplt.figure(refwidth=1.8)
axs = fig.subplots(array)
axs.format(
    abc=True,
    abcloc="ul",
    suptitle="Complex subplot grid",
    xlabel="xlabel",
    ylabel="ylabel",
)
axs[2].plot(data, lw=2)
# fig.save('~/example2.png')  # save the figure
# fig.savefig('~/example2.png')  # alternative


# %%
# Really complex grid
import numpy as np
import ultraplot as uplt

state = np.random.RandomState(51423)
data = 2 * (state.rand(100, 5) - 0.5).cumsum(axis=0)
array = [  # the "picture" (1 == subplot A, 2 == subplot B, etc.)
    [1, 1, 2],
    [1, 1, 6],
    [3, 4, 4],
    [3, 5, 5],
]
fig, axs = uplt.subplots(array, figwidth=5, span=False)
axs.format(
    suptitle="Really complex subplot grid", xlabel="xlabel", ylabel="ylabel", abc=True
)
axs[0].plot(data, lw=2)
fig.show()
# fig.save('~/example3.png')  # save the figure
# fig.savefig('~/example3.png')  # alternative

# %%
# Using a GridSpec
import numpy as np
import ultraplot as uplt

state = np.random.RandomState(51423)
data = 2 * (state.rand(100, 5) - 0.5).cumsum(axis=0)
gs = uplt.GridSpec(nrows=2, ncols=2, pad=1)
fig = uplt.figure(span=False, refwidth=2)
ax = fig.subplot(gs[:, 0])
ax.plot(data, lw=2)
ax = fig.subplot(gs[0, 1])
ax = fig.subplot(gs[1, 1])
fig.format(
    suptitle="Subplot grid with a GridSpec", xlabel="xlabel", ylabel="ylabel", abc=True
)
# fig.save('~/example4.png')  # save the figure
# fig.savefig('~/example4.png')  # alternative

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_subplotgrid:
#
# Multiple subplots
# -----------------
#
# If you create subplots all-at-once with e.g. :func:`~ultraplot.ui.subplots`,
# UltraPlot returns a :class:`~ultraplot.gridspec.SubplotGrid` of subplots. This list-like,
# array-like object provides some useful features and unifies the behavior of the
# three possible return types used by :func:`matplotlib.pyplot.subplots`:
#
# * :class:`~ultraplot.gridspec.SubplotGrid` behaves like a scalar when it is singleton.
#   In other words, if you make a single subplot with ``fig, axs = uplt.subplots()``,
#   then ``axs[0].method(...)`` is equivalent to ``axs.method(...)``.
# * :class:`~ultraplot.gridspec.SubplotGrid` permits list-like 1D indexing, e.g. ``axs[1]``
#   to return the second subplot. The subplots in the grid are sorted by
#   :func:`~ultraplot.axes.Axes.number` (see :ref:`this page <ug_abc>` for details
#   on changing the :func:`~ultraplot.axes.Axes.number` order).
# * :class:`~ultraplot.gridspec.SubplotGrid` permits array-like 2D indexing, e.g.
#   ``axs[1, 0]`` to return the subplot in the second row, first column, or
#   ``axs[:, 0]`` to return a :class:`~ultraplot.gridspec.SubplotGrid` of every subplot
#   in the first column. The 2D indexing is powered by the underlying
#   :func:`~ultraplot.gridspec.SubplotGrid.gridspec`.
#
# :class:`~ultraplot.gridspec.SubplotGrid` includes methods for working
# simultaneously with different subplots. Currently, this includes
# the commands :func:`~ultraplot.gridspec.SubplotGrid.format`,
# :func:`~ultraplot.gridspec.SubplotGrid.panel_axes`,
# :func:`~ultraplot.gridspec.SubplotGrid.inset_axes`,
# :func:`~ultraplot.gridspec.SubplotGrid.altx`, and :func:`~ultraplot.gridspec.SubplotGrid.alty`.
# In the below example, we use :func:`~ultraplot.gridspec.SubplotGrid.format` on the grid
# returned by :func:`~ultraplot.ui.subplots` to format different subgroups of subplots
# (:ref:`see below <ug_format>` for more on the format command).
#
# .. note::
#
#    If you create subplots one-by-one with :func:`~ultraplot.figure.Figure.subplot` or
#    :func:`~ultraplot.figure.Figure.add_subplot`, a :class:`~ultraplot.gridspec.SubplotGrid`
#    containing the numbered subplots is available via the
#    :class:`~ultraplot.figure.Figure.subplotgrid` property. As with subplots made
#    all-at-once, the subplots in the grid are sorted by :func:`~ultraplot.axes.Axes.number`.

# %%
import ultraplot as uplt
import numpy as np

state = np.random.RandomState(51423)

# Selected subplots in a simple grid
fig, axs = uplt.subplots(ncols=4, nrows=4, refwidth=1.2, span=True)
axs.format(xlabel="xlabel", ylabel="ylabel", suptitle="Simple SubplotGrid")
axs.format(grid=False, xlim=(0, 50), ylim=(-4, 4))
axs[:, 0].format(facecolor="blush", edgecolor="gray7", linewidth=1)  # eauivalent
axs[:, 0].format(fc="blush", ec="gray7", lw=1)
axs[0, :].format(fc="sky blue", ec="gray7", lw=1)
axs[0].format(ec="black", fc="gray5", lw=1.4)
axs[1:, 1:].format(fc="gray1")
for ax in axs[1:, 1:]:
    ax.plot((state.rand(50, 5) - 0.5).cumsum(axis=0), cycle="Grays", lw=2)

# Selected subplots in a complex grid
fig = uplt.figure(refwidth=1, refnum=5, span=False)
axs = fig.subplots([[1, 1, 2], [3, 4, 2], [3, 4, 5]], hratios=[2.2, 1, 1])
axs.format(xlabel="xlabel", ylabel="ylabel", suptitle="Complex SubplotGrid")
axs[0].format(ec="black", fc="gray1", lw=1.4)
axs[1, 1:].format(fc="blush")
axs[1, :1].format(fc="sky blue")
axs[-1, -1].format(fc="gray4", grid=False)
axs[0].plot((state.rand(50, 10) - 0.5).cumsum(axis=0), cycle="Grays_r", lw=2)


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_plots:
#
# Plotting stuff
# --------------
#
# Matplotlib includes `two different interfaces
# <https://matplotlib.org/stable/api/index.html>`__ for plotting stuff:
# a python-style object-oriented interface with axes-level commands
# like :method:`matplotlib.axes.Axes.plot`, and a MATLAB-style :mod:`~matplotlib.pyplot` interface
# with global commands like :func:`matplotlib.pyplot.plot` that track the "current" axes.
# UltraPlot builds upon the python-style interface using the `~ultraplot.axes.PlotAxes`
# class. Since every axes used by UltraPlot is a child of :class:`~ultraplot.axes.PlotAxes`, we
# are able to add features directly to the axes-level commands rather than relying
# on a separate library of commands  (note that while some of these features may be
# accessible via :mod:`~matplotlib.pyplot` commands, this is not officially supported).
#
# For the most part, the features added by :class:`~ultraplot.axes.PlotAxes` represent
# a *superset* of matplotlib. If you are not interested, you can use the plotting
# commands just like you would in matplotlib. Some of the core added features include
# more flexible treatment of :ref:`data arguments <ug_1dstd>`, recognition of
# :ref:`xarray and pandas <ug_1dintegration>` data structures, integration with
# UltraPlot's :ref:`colormap <ug_apply_cmap>` and :ref:`color cycle <ug_apply_cycle>`
# tools, and on-the-fly :ref:`legend and colorbar generation <ug_guides_plot>`.
# In the below example, we create a 4-panel figure with the
# familiar "1D" plotting commands :func:`~ultraplot.axes.PlotAxes.plot` and
# :func:`~ultraplot.axes.PlotAxes.scatter`, along with the "2D" plotting commands
# :func:`~ultraplot.axes.PlotAxes.pcolormesh` and :func:`~ultraplot.axes.PlotAxes.contourf`.
# See the :ref:`1D plotting <ug_1dplots>` and :ref:`2D plotting <ug_2dplots>`
# sections for details on the features added by UltraPlot.


# %%
import ultraplot as uplt
import numpy as np

# Sample data
N = 20
state = np.random.RandomState(51423)
data = N + (state.rand(N, N) - 0.55).cumsum(axis=0).cumsum(axis=1)

# Example plots
cycle = uplt.Cycle("greys", left=0.2, N=5)
fig, axs = uplt.subplots(ncols=2, nrows=2, figwidth=5, share=False)
axs[0].plot(data[:, :5], linewidth=2, linestyle="--", cycle=cycle)
axs[1].scatter(data[:, :5], marker="x", cycle=cycle)
axs[2].pcolormesh(data, cmap="greys")
m = axs[3].contourf(data, cmap="greys")
axs.format(
    abc="a.",
    titleloc="l",
    title="Title",
    xlabel="xlabel",
    ylabel="ylabel",
    suptitle="Quick plotting demo",
)
fig.colorbar(m, loc="b", label="label")


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_format:
#
# Formatting stuff
# ----------------
#
# Matplotlib includes `two different interfaces
# <https://matplotlib.org/stable/api/index.html>`__ for formatting stuff:
# a "python-style" object-oriented interface with instance-level commands
# like :func:`matplotlib.axes.Axes.set_title`, and a "MATLAB-style" interface
# that tracks current axes and provides global commands like
# :func:`matplotlib.pyplot.title`.
#
# UltraPlot provides the ``format`` command as an
# alternative "python-style" command for formatting a variety of plot elements.
# While matplotlib's one-liner commands still work, ``format`` only needs to be
# called once and tends to cut down on boilerplate code. You can call
# ``format`` manually or pass ``format`` parameters to axes-creation commands
# like :func:`~ultraplot.figure.Figure.subplots`, :func:`~ultraplot.figure.Figure.add_subplot`,
# :func:`~ultraplot.axes.Axes.inset_axes`, :func:`~ultraplot.axes.Axes.panel_axes`, and
# :func:`~ultraplot.axes.CartesianAxes.altx` or :func:`~ultraplot.axes.CartesianAxes.alty`. The
# keyword arguments accepted by ``format`` can be grouped as follows:
#
# * Figure settings. These are related to row labels, column labels, and
#   figure "super" titles -- for example, ``fig.format(suptitle='Super title')``.
#   See :func:`~ultraplot.figure.Figure.format` for details.
#
# * General axes settings. These are related to background patches,
#   a-b-c labels, and axes titles -- for example, ``ax.format(title='Title')``
#   See :func:`~ultraplot.axes.Axes.format` for details.
#
# * Cartesian axes settings (valid only for :class:`~ultraplot.axes.CartesianAxes`).
#   These are related to *x* and *y* axis ticks, spines, bounds, and labels --
#   for example, ``ax.format(xlim=(0, 5))`` changes the x axis bounds.
#   See :func:`~ultraplot.axes.CartesianAxes.format` and
#   :ref:`this section <ug_cartesian>` for details.
#
# * Polar axes settings (valid only for :class:`~ultraplot.axes.PolarAxes`).
#   These are related to azimuthal and radial grid lines, bounds, and labels --
#   for example, ``ax.format(rlim=(0, 10))`` changes the radial bounds.
#   See :func:`~ultraplot.axes.PolarAxes.format`
#   and :ref:`this section <ug_polar>` for details.
#
# * Geographic axes settings (valid only for :class:`~ultraplot.axes.GeoAxes`).
#   These are related to map bounds, meridian and parallel lines and labels,
#   and geographic features -- for example, ``ax.format(latlim=(0, 90))``
#   changes the meridional bounds. See :func:`~ultraplot.axes.GeoAxes.format`
#   and :ref:`this section <ug_geoformat>` for details.
#
# * :func:`~ultraplot.config.rc` settings. Any keyword matching the name
#   of an rc setting is locally applied to the figure and axes.
#   If the name has "dots", you can pass it as a keyword argument with
#   the "dots" omitted, or pass it to `rc_kw` in a dictionary. For example, the
#   default a-b-c label location is controlled by :rcraw:`abc.loc`. To change
#   this for an entire figure, you can use ``fig.format(abcloc='right')``
#   or ``fig.format(rc_kw={'abc.loc': 'right'})``.
#   See :ref:`this section <ug_config>` for more on rc settings.
#
# A ``format`` command is available on every figure and axes.
# :func:`~ultraplot.figure.Figure.format` accepts both figure and axes
# settings (applying them to each numbered subplot by default).
# Similarly, :func:`~ultraplot.axes.Axes.format` accepts both axes and figure
# settings. There is also a :func:`~ultraplot.gridspec.SubplotGrid.format`
# command that can be used to change settings for a subset of
# subplots -- for example, ``axs[:2].format(xtickminor=True)``
# turns on minor ticks for the first two subplots (see
# :ref:`this section <ug_subplotgrid>` for more on subplot grids).
# The below example shows the many keyword arguments accepted
# by ``format``, and demonstrates how ``format`` can be
# used to succinctly and efficiently customize plots.

# %%
import ultraplot as uplt
import numpy as np

fig, axs = uplt.subplots(ncols=2, nrows=2, refwidth=2, share=False)
state = np.random.RandomState(51423)
N = 60
x = np.linspace(1, 10, N)
y = (state.rand(N, 5) - 0.5).cumsum(axis=0)
axs[0].plot(x, y, linewidth=1.5)
axs.format(
    suptitle="Format command demo",
    abc="A.",
    abcloc="ul",
    title="Main",
    ltitle="Left",
    rtitle="Right",  # different titles
    ultitle="Title 1",
    urtitle="Title 2",
    lltitle="Title 3",
    lrtitle="Title 4",
    toplabels=("Column 1", "Column 2"),
    leftlabels=("Row 1", "Row 2"),
    xlabel="xaxis",
    ylabel="yaxis",
    xscale="log",
    xlim=(1, 10),
    xticks=1,
    ylim=(-3, 3),
    yticks=uplt.arange(-3, 3),
    yticklabels=("a", "bb", "c", "dd", "e", "ff", "g"),
    ytickloc="both",
    yticklabelloc="both",
    xtickdir="inout",
    xtickminor=False,
    ygridminor=True,
)

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_rc:
#
# Settings and styles
# -------------------
#
# A dictionary-like object named :func:`~ultraplot.config.rc` is created when you import
# UltraPlot. :func:`~ultraplot.config.rc` is similar to the matplotlib :data:`~matplotlib.rcParams`
# dictionary, but can be used to change both `matplotlib settings
# <https://matplotlib.org/stable/tutorials/introductory/customizing.html>`__ and
# :ref:`ultraplot settings <ug_rcUltraPlot>`. The matplotlib-specific settings are
# stored in :func:`~ultraplot.config.rc_matplotlib` (our name for :data:`~matplotlib.rcParams`) and
# the UltraPlot-specific settings are stored in :class:`~ultraplot.config.rc_ultraplot`.
# UltraPlot also includes a :rcraw:`style` setting that can be used to
# switch between `matplotlib stylesheets
# <https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html>`__.
# See the :ref:`configuration section <ug_config>` for details.
#
# To modify a setting for just one subplot or figure, you can pass it to
# :func:`~ultraplot.axes.Axes.format` or :func:`~ultraplot.figure.Figure.format`. To temporarily
# modify setting(s) for a block of code, use :func:`~ultraplot.config.Configurator.context`.
# To modify setting(s) for the entire python session, just assign it to the
# :func:`~ultraplot.config.rc` dictionary or use :func:`~ultraplot.config.Configurator.update`.
# To reset everything to the default state, use :func:`~ultraplot.config.Configurator.reset`.
# See the below example.


# %%
import ultraplot as uplt
import numpy as np

# Update global settings in several different ways
uplt.rc.metacolor = "gray6"
uplt.rc.update({"fontname": "Source Sans Pro", "fontsize": 11})
uplt.rc["figure.facecolor"] = "gray3"
uplt.rc.axesfacecolor = "gray4"
# uplt.rc.save()  # save the current settings to ~/.ultraplotrc

# Apply settings to figure with context()
with uplt.rc.context({"suptitle.size": 13}, toplabelcolor="gray6", metawidth=1.5):
    fig = uplt.figure(figwidth=6, sharey="limits", span=False)
    axs = fig.subplots(ncols=2)

# Plot lines with a custom cycler
N, M = 100, 7
state = np.random.RandomState(51423)
values = np.arange(1, M + 1)
cycle = uplt.get_colors("grays", M - 1) + ["red"]
for i, ax in enumerate(axs):
    data = np.cumsum(state.rand(N, M) - 0.5, axis=0)
    lines = ax.plot(data, linewidth=3, cycle=cycle)

# Apply settings to axes with format()
axs.format(
    grid=False,
    xlabel="xlabel",
    ylabel="ylabel",
    toplabels=("Column 1", "Column 2"),
    suptitle="Rc settings demo",
    suptitlecolor="gray7",
    abc="[A]",
    abcloc="l",
    title="Title",
    titleloc="r",
    titlecolor="gray7",
)

# Reset persistent modifications from head of cell
uplt.rc.reset()


# %%
import ultraplot as uplt
import numpy as np

# uplt.rc.style = 'style'  # set the style everywhere

# Sample data
state = np.random.RandomState(51423)
data = state.rand(10, 5)

# Set up figure
fig, axs = uplt.subplots(ncols=2, nrows=2, span=False, share=False)
axs.format(suptitle="Stylesheets demo")
styles = ("ggplot", "seaborn", "538", "bmh")

# Apply different styles to different axes with format()
for ax, style in zip(axs, styles):
    ax.format(style=style, xlabel="xlabel", ylabel="ylabel", title=style)
    ax.plot(data, linewidth=3)
