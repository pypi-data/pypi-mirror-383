# -*- coding: utf-8 -*-
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
#
# .. _polar: https://matplotlib.org/3.1.0/gallery/pie_and_polar_charts/polar_demo.html
#
# .. _cartopy: https://cartopy.readthedocs.io/stable/
#
# .. _basemap: https://matplotlib.org/basemap/index.html
#
# .. _ug_proj:
#
# Geographic and polar axes
# =========================
#
# This section documents several useful features for working with `polar`_ plots
# and :ref:`geographic projections <ug_geo>`. The geographic features are powered by
# `cartopy`_ (or, optionally, `basemap`_). Note that these features are *optional* --
# installation of cartopy or basemap are not required to use UltraPlot.
#
# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_polar:
#
# Polar axes
# ----------
#
# To create `polar axes <polar_>`_, pass ``proj='polar'`` to an axes-creation
# command like :meth:`ultraplot.figure.Figure.add_subplot`. Polar axes are represented with the
# :class:`~ultraplot.axes.PolarAxes` subclass, which has its own :func:`~ultraplot.axes.PolarAxes.format`
# command. :meth:`ultraplot.axes.PolarAxes.format` facilitates polar-specific modifications
# like changing the central radius `r0`, the zero azimuth location `theta0`,
# and the positive azimuthal direction `thetadir`. It also supports toggling and
# configuring the "major" and "minor" gridline locations with `grid`, `rlocator`,
# `thetalocator`, `gridminor`, `rminorlocator`, and `thetaminorlocator` and formatting
# the gridline labels with `rformatter` and `thetaformatter` (analogous to `xlocator`,
# `xformatter`, and `xminorlocator` used by :func:`ultraplot.axes.CartesianAxes.format`),
# and creating "annular" or "sector" plots by changing the radial or azimuthal
# bounds `rlim` and `thetalim`. Finally, since :meth:`ultraplot.axes.PolarAxes.format`
# calls :meth:`ultraplot.axes.Axes.format`, it can be used to add axes titles, a-b-c
# labels, and figure titles.
#
# For details, see :meth:`ultraplot.axes.PolarAxes.format`.

# %%
import ultraplot as uplt
import numpy as np

N = 200
state = np.random.RandomState(51423)
x = np.linspace(0, 2 * np.pi, N)[:, None] + np.arange(5) * 2 * np.pi / 5
y = 100 * (state.rand(N, 5) - 0.3).cumsum(axis=0) / N
fig, axs = uplt.subplots([[1, 1, 2, 2], [0, 3, 3, 0]], proj="polar", share=0)
axs.format(
    suptitle="Polar axes demo",
    linewidth=1,
    titlepad="1em",
    ticklabelsize=9,
    rlines=0.5,
    rlim=(0, 19),
)
for ax in axs:
    ax.plot(x, y, cycle="default", zorder=0, lw=3)

# Standard polar plot
axs[0].format(
    title="Normal plot",
    thetaformatter="tau",
    rlabelpos=225,
    rlines=uplt.arange(5, 30, 5),
    edgecolor="red8",
    tickpad="1em",
)

# Sector plot
axs[1].format(
    title="Sector plot",
    thetadir=-1,
    thetalines=90,
    thetalim=(0, 270),
    theta0="N",
    rlim=(0, 22),
    rlines=uplt.arange(5, 30, 5),
)

# Annular plot
axs[2].format(
    title="Annular plot",
    thetadir=-1,
    thetalines=20,
    gridcolor="red",
    r0=-20,
    rlim=(0, 22),
    rformatter="null",
    rlocator=2,
)

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_geo:
#
# Geographic axes
# ---------------
#
# To create geographic axes, pass ``proj='name'`` to an axes-creation command like
# :meth:`ultraplot.figure.Figure.add_subplot`, where ``name`` is any valid :ref:`PROJ projection
# name <proj_table>`. Alternatively, you can pass a :class:`cartopy.crs.Projection` or
# :class:`~mpl_toolkits.basemap.Basemap` instance returned by the :class:`~ultraplot.constructor.Proj`
# :ref:`constructor function <why_constructor>` to `proj` (see below for details). If
# you want to create your subplots :ref:`all-at-once <ug_subplot>` with e.g.
# :func:`~ultraplot.ui.subplots` but need different projections for each subplot, you can pass
# a list or dictionary to the `proj` keyword (e.g., ``proj=('cartesian', 'pcarree')``
# or ``proj={2: 'pcarree'}`` -- see :func:`~ultraplot.figure.Figure.subplots` for details).
# Geographic axes are represented with the :class:`~ultraplot.axes.GeoAxes` subclass, which
# has its own :meth:`~ultraplot.axes.GeoAxes.format` command. :meth:`ultraplot.axes.GeoAxes.format`
# facilitates :ref:`geographic-specific modifications <ug_geoformat>` like meridional
# and parallel gridlines and land mass outlines. The syntax is very similar to
# :func:`ultraplot.axes.CartesianAxes.format`.
#  .. important::
#           The internal reference system used for plotting in ultraplot is **PlateCarree**.
#           External libraries, such as `contextily`, may use different internal reference systems,
#           such as **EPSG:3857** (Web Mercator). When interfacing with such libraries, it is important
#           to provide the appropriate `transform` parameter to ensure proper alignment between coordinate systems.
# Note that the `proj` keyword and several of
# the :func:`~ultraplot.axes.GeoAxes.format` keywords are inspired by the basemap API.
# In the below example, we create and format a very simple geographic plot.

# %%
# Use an on-the-fly projection
import ultraplot as uplt

fig = uplt.figure(refwidth=3, share=0)
axs = fig.subplots(
    nrows=2,
    proj="robin",
    proj_kw={"lon0": 150},
)
axs.format(
    suptitle="Figure with single projection",
    land=True,
    latlines=30,
    lonlines=60,
)

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_backends:
#
# Geographic backends
# -------------------
#
# The :class:`~ultraplot.axes.GeoAxes` class uses either `cartopy`_ or `basemap`_ as "backends"
# to :ref:`format the axes <ug_geoformat>` and :ref:`plot stuff <ug_geoplot>` in
# the axes. A few details:
#
# * Cartopy is the default backend. When you request projection names with cartopy
#   as the backend (or pass a :class:`cartopy.crs.Projection` to the `proj` keyword), the
#   returned axes is a subclass of :class:`cartopy.mpl.geoaxes.GeoAxes`. Under the hood,
#   invoking :func:`~ultraplot.axes.GeoAxes.format` with cartopy as the backend changes map
#   bounds using :meth:`~cartopy.mpl.geoaxes.GeoAxes.set_extent`, adds major and minor
#   gridlines using :mod:`~cartopy.mpl.geoaxes.GeoAxes.gridlines`, and adds geographic
#   features using :meth:`~cartopy.mpl.geoaxes.GeoAxes.add_feature`. If you prefer, you can
#   use the standard :class:`cartopy.mpl.geoaxes.GeoAxes` methods just like you would in
#   cartopy. If you need to use the underlying :class:`~cartopy.crs.Projection` instance, it
#   is available via the :func:`~ultraplot.axes.GeoAxes.projection` attribute. If you want
#   to work with the projection classes directly, they are available in the
#   top-level namespace (e.g., ``proj=uplt.PlateCarre()`` is allowed).
#
# * Basemap is an alternative backend. To use basemap, set :rcraw:`geo.backend` to
#   ``'basemap'`` or pass ``backend='basemap'`` to the axes-creation command. When
#   you request a projection name with basemap as the backend (or pass a
#   :class:`~mpl_toolkits.basemap.Basemap` to the `proj` keyword), the returned axes
#   redirects the plotting methods plot, scatter, contour, contourf, pcolor,
#   pcolormesh, quiver, streamplot, and barb to the identically named methods on
#   the :class:`~mpl_toolkits.basemap.Basemap` instance. This means you can work
#   with the standard axes plotting methods rather than the basemap methods --
#   just like cartopy. Under the hood, invoking :func:`~ultraplot.axes.GeoAxes.format`
#   with basemap as the backend adds major and minor gridlines using
#   :meth:`~mpl_toolkits.basemap.Basemap.drawmeridians` and
#   :meth:`~mpl_toolkits.basemap.Basemap.drawparallels` and adds geographic features
#   using methods like :meth:`~mpl_toolkits.basemap.Basemap.fillcontinents`
#   and :meth:`~mpl_toolkits.basemap.Basemap.drawcoastlines`. If you need to
#   use the underlying :class:`~mpl_toolkits.basemap.Basemap` instance, it is
#   available as the :attr:`~ultraplot.axes.GeoAxes.projection` attribute.
#
# Together, these features let you work with geophysical data without invoking
# verbose cartopy classes like :class:`~cartopy.crs.LambertAzimuthalEqualArea` or
# keeping track of separate :class:`~mpl_toolkits.basemap.Basemap` instances. This
# considerably reduces the amount of code needed to make complex geographic
# plots. In the below examples, we create a variety of plots using both
# cartopy and basemap as backends.
#
# .. important::
#
#    * By default, UltraPlot bounds polar cartopy projections like
#      :classs:`~cartopy.crs.NorthPolarStereo` at the equator and gives non-polar cartopy
#      projections global extent by calling :meth:`~cartopy.mpl.geoaxes.GeoAxes.set_global`.
#      This is a deviation from cartopy, which determines map boundaries automatically
#      based on the coordinates of the plotted content. To revert to cartopy's
#      default behavior, set :rcraw:`geo.extent` to ``'auto`` or pass ``extent='auto'``
#      to :func:`~ultraplot.axes.GeoAxes.format`.
#    * By default, UltraPlot gives circular boundaries to polar cartopy and basemap
#      projections like :class:`~cartopy.crs.NorthPolarStereo` (see `this example
#      <https://cartopy.readthedocs.io/stable/gallery/lines_and_polygons/always_circular_stereo.html>`__
#      from the cartopy website). To disable this feature, set :rcraw:`geo.round` to
#      ``False`` or pass ``round=False` to :func:`~ultraplot.axes.GeoAxes.format`. Please note
#      that older versions of cartopy cannot add gridlines to maps bounded by circles.
#    * To make things more consistent, the :class:`~ultraplot.constructor.Proj` constructor
#      function lets you supply native `PROJ <https://proj.org>`__ keyword names
#      for the cartopy :class:`~cartopy.crs.Projection` classes (e.g., `lon0` instead
#      of `central_longitude`) and instantiates :class:`~mpl_toolkits.basemap.Basemap`
#      projections with sensible default PROJ parameters rather than raising an error
#      when they are omitted (e.g., ``lon0=0`` as the default for most projections).
#
# .. warning::
#    The `basemap`_ package is now being actively maintained again with a short hiatus for a few years. We originally
#    included basemap support because its gridline labeling was more powerful
#    than cartopy gridline labeling. While cartopy gridline labeling has
#    significantly improved since version 0.18, UltraPlot continues to support
#    both mapping libraries to give users flexibility in their visualization choices.

# %%
import ultraplot as uplt

fig = uplt.figure(share=0)

# Add projections
gs = uplt.GridSpec(ncols=2, nrows=3, hratios=(1, 1, 1.4))
for i, proj in enumerate(("cyl", "hammer", "npstere")):
    ax1 = fig.subplot(gs[i, 0], proj=proj)  # default cartopy backend
    ax2 = fig.subplot(gs[i, 1], proj=proj, backend="basemap")  # basemap backend

# Format projections
axs = fig.subplotgrid
axs.format(
    land=True,
    suptitle="Figure with several projections",
    toplabels=("Cartopy examples", "Basemap examples"),
    toplabelweight="normal",
    latlines=30,
    lonlines=60,
)
axs[:2].format(lonlabels="b", latlabels="r")  # or lonlabels=True, lonlabels='bottom',
axs[2:4].format(lonlabels=False, latlabels="both")
axs[4:].format(lonlabels="all", lonlines=30)
uplt.rc.reset()


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_geoplot:
#
# Plotting in projections
# -----------------------
#
# In UltraPlot, plotting with :class:`~ultraplot.axes.GeoAxes` is just like plotting
# with :class:`~ultraplot.axes.CartesianAxes`. UltraPlot makes longitude-latitude
# (i.e., Plate Carrée) coordinates the *default* coordinate system for all plotting
# commands by internally passing ``transform=ccrs.PlateCarree()`` to cartopy commands
# and ``latlon=True`` to basemap commands. And again, when `basemap`_ is the backend,
# plotting is done "cartopy-style" by calling methods from the `ultraplot.axes.GeoAxes`
# instance rather than the :class:`~mpl_toolkits.basemap.Basemap` instance.
#
# To ensure that a 2D :class:`~ultraplot.axes.PlotAxes` command like
# :func:`~ultraplot.axes.PlotAxes.contour` or :func:`~ultraplot.axes.PlotAxes.pcolor`
# fills the entire globe, simply pass ``globe=True`` to the command.
# This interpolates the data to the North and South poles and across the longitude
# seam before plotting. This is a convenient and succinct alternative to cartopy's
# :meth:`~cartopy.util.add_cyclic_point` and basemap's :meth:`~mpl_toolkits.basemap.addcyclic`.
#
# To draw content above or underneath a given geographic feature, simply change
# the `zorder <https://matplotlib.org/3.1.1/gallery/misc/zorder_demo.html>`__
# property for that feature. For example, to draw land patches on top of all plotted
# content as a "land mask" you can use ``ax.format(land=True, landzorder=4)`` or set
# ``uplt.rc['land.zorder'] = 4`` (see the :ref:`next section <ug_geoformat>`
# for details).

# %%
import ultraplot as uplt
import numpy as np

# Fake data with unusual longitude seam location and without coverage over poles
offset = -40
lon = uplt.arange(offset, 360 + offset - 1, 60)
lat = uplt.arange(-60, 60 + 1, 30)
state = np.random.RandomState(51423)
data = state.rand(len(lat), len(lon))

# Plot data both without and with globe=True
for globe in (False, True):
    string = "with" if globe else "without"
    gs = uplt.GridSpec(nrows=2, ncols=2)
    fig = uplt.figure(refwidth=2.5, share=0)
    for i, ss in enumerate(gs):
        cmap = ("sunset", "sunrise")[i % 2]
        backend = ("cartopy", "basemap")[i % 2]
        ax = fig.subplot(ss, proj="kav7", backend=backend)
        if i > 1:
            ax.pcolor(lon, lat, data, cmap=cmap, globe=globe, extend="both")
        else:
            m = ax.contourf(lon, lat, data, cmap=cmap, globe=globe, extend="both")
            fig.colorbar(m, loc="b", span=i + 1, label="values", extendsize="1.7em")
    fig.format(
        suptitle=f"Geophysical data {string} global coverage",
        toplabels=("Cartopy example", "Basemap example"),
        leftlabels=("Filled contours", "Grid boxes"),
        toplabelweight="normal",
        leftlabelweight="normal",
        coast=True,
        lonlines=90,
        abc="A.",
        abcloc="ul",
        abcborder=False,
    )


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_geoformat:
#
# Formatting projections
# ----------------------
#
# The :meth:`~ultraplot.axes.GeoAxes.format` command facilitates geographic-specific axes
# modifications. It can toggle and configure the "major" and "minor" longitude and
# latitude gridline locations using the `grid`, `lonlocator`, `latlocator`, `gridminor`,
# `lonminorlocator`, and `latminorlocator` keys, and configure gridline label formatting
# with `lonformatter` and `latformatter` (analogous to `xlocator`, `xminorlocator`,
# and `xformatter` used by :meth:`ultraplot.axes.CartesianAxes.format`). By default, inline
# cartopy labels and cartopy label rotation are turned off, but inline labels can
# be turned on using ``loninline=True``, ``latinline=True``, or ``inlinelabels=True``
# or by setting :rcraw:`grid.inlinelabels` to ``True``, and label rotation can be
# turned on using ``rotatelabels=True`` or by setting :rcraw:`grid.rotatelabels`
# to ``True``. The padding between the map edge and the labels can be changed
# using `labelpad` or by changing :rcraw:`grid.labelpad`.
#
# :meth:`~ultraplot.axes.GeoAxes.format` can also set the cartopy projection bounding longitudes
# and latitudes with `lonlim` and `latlim` (analogous to `xlim` and `ylim`), set the
# latitude bound for circular polar projections using `boundinglat`, and toggle and
# configure geographic features like land masses, coastlines, and administrative
# borders using :ref:`settings <rc_UltraPlot>` like `land`, `landcolor`, `coast`,
# `coastcolor`, and `coastlinewidth`. Finally, since :meth:`ultraplot.axes.GeoAxes.format`
# calls :meth:`ultraplot.axes.Axes.format`, it can be used to add axes titles, a-b-c labels,
# and figure titles, just like :func:`ultraplot.axes.CartesianAxes.format`. UltraPlot also adds the ability to add tick marks for longitude and latitude using the keywords `lontick` and `lattick` for rectilinear projections only. This can enhance contrast and readability under some conditions, e.g. when overlaying contours.
#
# For details, see the :meth:`ultraplot.axes.GeoAxes.format` documentation.

# %%
import ultraplot as uplt

gs = uplt.GridSpec(ncols=3, nrows=2, wratios=(1, 1, 1.2), hratios=(1, 1.2))
fig = uplt.figure(refwidth=4, share=0)

# Styling projections in different ways
ax = fig.subplot(gs[0, :2], proj="eqearth")
ax.format(
    title="Equal earth",
    land=True,
    landcolor="navy",
    facecolor="pale blue",
    coastcolor="gray5",
    borderscolor="gray5",
    innerborderscolor="gray5",
    gridlinewidth=1.5,
    gridcolor="gray5",
    gridalpha=0.5,
    gridminor=True,
    gridminorlinewidth=0.5,
    coast=True,
    borders=True,
    borderslinewidth=0.8,
)
ax = fig.subplot(gs[0, 2], proj="ortho")
ax.format(
    title="Orthographic",
    reso="med",
    land=True,
    coast=True,
    latlines=10,
    lonlines=15,
    landcolor="mushroom",
    suptitle="Projection axes formatting demo",
    facecolor="petrol",
    coastcolor="charcoal",
    coastlinewidth=0.8,
    gridlinewidth=1,
)
ax = fig.subplot(gs[1, :], proj="wintri")
ax.format(
    land=True,
    facecolor="ocean blue",
    landcolor="bisque",
    title="Winkel tripel",
    lonlines=60,
    latlines=15,
    gridlinewidth=0.8,
    gridminor=True,
    gridminorlinestyle=":",
    lonlabels=True,
    latlabels="r",
    loninline=True,
    gridlabelcolor="gray8",
    gridlabelsize="med-large",
)
fig.format(
    suptitle="Projection axes formatting demo",
    toplabels=("Column 1", "Column 2"),
    abc="A.",
    abcloc="ul",
    abcborder=False,
    linewidth=1.5,
)


# %% [raw] raw_mimetype="text/restructuredtext"
# .. _ug_zoom:
#
# Zooming into projections
# ------------------------
#
# To zoom into cartopy projections, use
# :meth:`~cartopy.mpl.geoaxes.GeoAxes.set_extent` or pass `lonlim`,
# `latlim`, or `boundinglat` to :meth:`~ultraplot.axes.GeoAxes.format`. The `boundinglat`
# keyword controls the circular latitude boundary for North Polar and
# South Polar Stereographic, Azimuthal Equidistant, Lambert Azimuthal
# Equal-Area, and Gnomonic projections. By default, UltraPlot tries to use the
# degree-minute-second cartopy locators and formatters made available in cartopy
# 0.18. You can switch from minute-second subintervals to traditional decimal
# subintervals by passing ``dms=False`` to :meth:`~ultraplot.axes.GeoAxes.format`
# or by setting :rcraw:`grid.dmslabels` to ``False``.
#
# To zoom into basemap projections, pass any of the `boundinglat`,
# `llcrnrlon`, `llcrnrlat`, `urcrnrlon`, `urcrnrlat`, `llcrnrx`, `llcrnry`,
# `urcrnrx`, `urcrnry`, `width`, or `height` keyword arguments to
# the :class:`~ultraplot.constructor.Proj` constructor function either directly or via
# the `proj_kw` :func:`~ultraplot.ui.subplots` keyword argument. You can also pass
# `lonlim` and `latlim` to :class:`~ultraplot.constructor.Proj` and these arguments
# will be used for `llcrnrlon`, `llcrnrlat`, etc. You cannot zoom into basemap
# projections with `format` after they have already been created.

# %%
import ultraplot as uplt

# Plate Carrée map projection
uplt.rc.reso = "med"  # use higher res for zoomed in geographic features
basemap = uplt.Proj("cyl", lonlim=(-20, 180), latlim=(-10, 50), backend="basemap")
fig, axs = uplt.subplots(nrows=2, refwidth=5, proj=("cyl", basemap), share=0)
axs.format(
    land=True,
    labels=True,
    lonlines=20,
    latlines=20,
    gridminor=True,
    suptitle="Zooming into projections",
)
axs[0].format(lonlim=(-140, 60), latlim=(-10, 50), labels=True)
axs[0].format(title="Cartopy example")
axs[1].format(title="Basemap example")

# %%
import ultraplot as uplt

# Pole-centered map projections
basemap = uplt.Proj("npaeqd", boundinglat=60, backend="basemap")
fig, axs = uplt.subplots(ncols=2, refwidth=2.7, proj=("splaea", basemap), share=0)
fig.format(suptitle="Zooming into polar projections")
axs.format(land=True, latmax=80)  # no gridlines poleward of 80 degrees
axs[0].format(boundinglat=-60, title="Cartopy example")
axs[1].format(title="Basemap example")

# %%
import ultraplot as uplt

# Zooming in on continents
fig = uplt.figure(refwidth=3, share=0)
ax = fig.subplot(121, proj="lcc", proj_kw={"lon0": 0})
ax.format(lonlim=(-20, 50), latlim=(30, 70), title="Cartopy example")
proj = uplt.Proj("lcc", lon0=-100, lat0=45, width=8e6, height=8e6, backend="basemap")
ax = fig.subplot(122, proj=proj)
ax.format(lonlines=20, title="Basemap example")
fig.format(suptitle="Zooming into specific regions", land=True)


# %%
import ultraplot as uplt

# Zooming in with cartopy degree-minute-second labels
# Set TeX Gyre Heros as the primary font but fall back to DejaVu Sans
uplt.rc["font.family"] = ["TeX Gyre Heros", "DejaVu Sans"]
uplt.rc.reso = "hi"
fig = uplt.figure(refwidth=2.5)
ax = fig.subplot(121, proj="cyl")
ax.format(lonlim=(-7.5, 2), latlim=(49.5, 59))
ax = fig.subplot(122, proj="cyl")
ax.format(lonlim=(-6, -2), latlim=(54.5, 58.5))
fig.format(
    land=True,
    labels=True,
    borders=True,
    borderscolor="white",
    suptitle="Cartopy degree-minute-second labels",
)
uplt.rc.reset()

# %% [raw] raw_mimetype="text/restructuredtext"
# .. _proj_included:
#
# Included projections
# --------------------
#
# The available `cartopy <https://cartopy.readthedocs.io/stable/>`__
# and `basemap <https://matplotlib.org/basemap/index.html>`__ projections are
# plotted below. The full table of projection names with links to the relevant
# `PROJ <https://proj.org>`__ documentation is found :ref:`here <proj_table>`.
#
# UltraPlot uses the cartopy API to add the Aitoff, Hammer, Winkel Tripel, and
# Kavrayskiy VII projections (i.e., ``'aitoff'``, ``'hammer'``, ``'wintri'``,
# and ``'kav7'``), as well as North and South polar versions of the Azimuthal
# Equidistant, Lambert Azimuthal Equal-Area, and Gnomonic projections (i.e.,
# ``'npaeqd'``, ``'spaeqd'``, ``'nplaea'``, ``'splaea'``, ``'npgnom'``, and
# ``'spgnom'``), modeled after cartopy's existing :class:`~cartopy.crs.NorthPolarStereo`
# and :class:`~cartopy.crs.SouthPolarStereo` projections.

# %%
import ultraplot as uplt

# Table of cartopy projections
projs = [
    "cyl",
    "merc",
    "mill",
    "lcyl",
    "tmerc",
    "robin",
    "hammer",
    "moll",
    "kav7",
    "aitoff",
    "wintri",
    "sinu",
    "geos",
    "ortho",
    "nsper",
    "aea",
    "eqdc",
    "lcc",
    "gnom",
    "npstere",
    "nplaea",
    "npaeqd",
    "npgnom",
    "igh",
    "eck1",
    "eck2",
    "eck3",
    "eck4",
    "eck5",
    "eck6",
]
fig, axs = uplt.subplots(ncols=3, nrows=10, figwidth=7, proj=projs, share=0)
axs.format(land=True, reso="lo", labels=False, suptitle="Table of cartopy projections")
for proj, ax in zip(projs, axs):
    ax.format(title=proj, titleweight="bold", labels=False)

# %%
import ultraplot as uplt

# Table of basemap projections
projs = [
    "cyl",
    "merc",
    "mill",
    "cea",
    "gall",
    "sinu",
    "eck4",
    "robin",
    "moll",
    "kav7",
    "hammer",
    "mbtfpq",
    "geos",
    "ortho",
    "nsper",
    "vandg",
    "aea",
    "eqdc",
    "gnom",
    "cass",
    "lcc",
    "npstere",
    "npaeqd",
    "nplaea",
]
fig, axs = uplt.subplots(
    ncols=3, nrows=8, figwidth=7, proj=projs, backend="basemap", share=0
)
axs.format(land=True, labels=False, suptitle="Table of basemap projections")
for proj, ax in zip(projs, axs):
    ax.format(title=proj, titleweight="bold", labels=False)
