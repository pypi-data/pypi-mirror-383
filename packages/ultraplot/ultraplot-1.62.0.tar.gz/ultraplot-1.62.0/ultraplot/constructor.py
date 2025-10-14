#!/usr/bin/env python3
"""
T"he constructor functions used to build class instances from simple shorthand arguments.
"""
# NOTE: These functions used to be in separate files like crs.py and
# ticker.py but makes more sense to group them together to ensure usage is
# consistent and so online documentation is easier to understand. Also in
# future version classes will not be imported into top-level namespace. This
# change will be easier to do with all constructor functions in separate file.
# NOTE: Used to include the raw variable names that define string keys as
# part of documentation, but this is redundant and pollutes the namespace.
# User should just inspect docstrings, use trial-error, or see online tables.
import copy
import os
import re
from functools import partial
from numbers import Number

import cycler
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.projections.polar as mpolar
import matplotlib.scale as mscale
import matplotlib.ticker as mticker
import numpy as np

from . import colors as pcolors
from . import proj as pproj
from . import scale as pscale
from . import ticker as pticker
from .config import rc
from .internals import ic  # noqa: F401
from .internals import (
    _not_none,
    _pop_props,
    _version_cartopy,
    _version_mpl,
    warnings,
)
from .utils import get_colors, to_hex, to_rgba

try:
    from mpl_toolkits.basemap import Basemap
except ImportError:
    Basemap = object
try:
    import cartopy.crs as ccrs
    from cartopy.crs import Projection
except ModuleNotFoundError:
    ccrs = None
    Projection = object

__all__ = [
    "Proj",
    "Locator",
    "Formatter",
    "Scale",
    "Colormap",
    "Norm",
    "Cycle",
    "Colors",  # deprecated
]

# Color cycle constants
# TODO: Also automatically truncate the 'bright' end of colormaps
# when building color cycles from colormaps? Or add simple option.
DEFAULT_CYCLE_SAMPLES = 10
DEFAULT_CYCLE_LUMINANCE = 90

# Normalizer registry
NORMS = {
    "none": mcolors.NoNorm,
    "null": mcolors.NoNorm,
    "div": pcolors.DivergingNorm,
    "diverging": pcolors.DivergingNorm,
    "segmented": pcolors.SegmentedNorm,
    "segments": pcolors.SegmentedNorm,
    "log": mcolors.LogNorm,
    "linear": mcolors.Normalize,
    "power": mcolors.PowerNorm,
    "symlog": mcolors.SymLogNorm,
}
if hasattr(mcolors, "TwoSlopeNorm"):
    NORMS["twoslope"] = mcolors.TwoSlopeNorm

# Locator registry
# NOTE: Will raise error when you try to use degree-minute-second
# locators with cartopy < 0.18.
LOCATORS = {
    "none": mticker.NullLocator,
    "null": mticker.NullLocator,
    "auto": mticker.AutoLocator,
    "log": mticker.LogLocator,
    "maxn": mticker.MaxNLocator,
    "linear": mticker.LinearLocator,
    "multiple": mticker.MultipleLocator,
    "fixed": mticker.FixedLocator,
    "index": pticker.IndexLocator,
    "discrete": pticker.DiscreteLocator,
    "discreteminor": partial(pticker.DiscreteLocator, minor=True),
    "symlog": mticker.SymmetricalLogLocator,
    "logit": mticker.LogitLocator,
    "minor": mticker.AutoMinorLocator,
    "date": mdates.AutoDateLocator,
    "microsecond": mdates.MicrosecondLocator,
    "second": mdates.SecondLocator,
    "minute": mdates.MinuteLocator,
    "hour": mdates.HourLocator,
    "day": mdates.DayLocator,
    "weekday": mdates.WeekdayLocator,
    "month": mdates.MonthLocator,
    "year": mdates.YearLocator,
    "lon": partial(pticker.LongitudeLocator, dms=False),
    "lat": partial(pticker.LatitudeLocator, dms=False),
    "deglon": partial(pticker.LongitudeLocator, dms=False),
    "deglat": partial(pticker.LatitudeLocator, dms=False),
}
if hasattr(mpolar, "ThetaLocator"):
    LOCATORS["theta"] = mpolar.ThetaLocator
if _version_cartopy >= "0.18":
    LOCATORS["dms"] = partial(pticker.DegreeLocator, dms=True)
    LOCATORS["dmslon"] = partial(pticker.LongitudeLocator, dms=True)
    LOCATORS["dmslat"] = partial(pticker.LatitudeLocator, dms=True)

# Formatter registry
# NOTE: Critical to use SimpleFormatter for cardinal formatters rather than
# AutoFormatter because latter fails with Basemap formatting.
# NOTE: Define cartopy longitude/latitude formatters with dms=True because that
# is their distinguishing feature relative to ultraplot formatter.
# NOTE: Will raise error when you try to use degree-minute-second
# formatters with cartopy < 0.18.
FORMATTERS = {  # note default LogFormatter uses ugly e+00 notation
    "none": mticker.NullFormatter,
    "null": mticker.NullFormatter,
    "auto": pticker.AutoFormatter,
    "date": mdates.AutoDateFormatter,
    "scalar": mticker.ScalarFormatter,
    "simple": pticker.SimpleFormatter,
    "fixed": mticker.FixedLocator,
    "index": pticker.IndexFormatter,
    "sci": pticker.SciFormatter,
    "sigfig": pticker.SigFigFormatter,
    "frac": pticker.FracFormatter,
    "func": mticker.FuncFormatter,
    "strmethod": mticker.StrMethodFormatter,
    "formatstr": mticker.FormatStrFormatter,
    "datestr": mdates.DateFormatter,
    "log": mticker.LogFormatterSciNotation,  # NOTE: this is subclass of Mathtext class
    "logit": mticker.LogitFormatter,
    "eng": mticker.EngFormatter,
    "percent": mticker.PercentFormatter,
    "e": partial(pticker.FracFormatter, symbol=r"$e$", number=np.e),
    "pi": partial(pticker.FracFormatter, symbol=r"$\pi$", number=np.pi),
    "tau": partial(pticker.FracFormatter, symbol=r"$\tau$", number=2 * np.pi),
    "lat": partial(pticker.SimpleFormatter, negpos="SN"),
    "lon": partial(pticker.SimpleFormatter, negpos="WE", wraprange=(-180, 180)),
    "deg": partial(pticker.SimpleFormatter, suffix="\N{DEGREE SIGN}"),
    "deglat": partial(pticker.SimpleFormatter, suffix="\N{DEGREE SIGN}", negpos="SN"),
    "deglon": partial(
        pticker.SimpleFormatter,
        suffix="\N{DEGREE SIGN}",
        negpos="WE",
        wraprange=(-180, 180),
    ),  # noqa: E501
    "math": mticker.LogFormatterMathtext,  # deprecated (use SciNotation subclass)
}
if hasattr(mpolar, "ThetaFormatter"):
    FORMATTERS["theta"] = mpolar.ThetaFormatter
if hasattr(mdates, "ConciseDateFormatter"):
    FORMATTERS["concise"] = mdates.ConciseDateFormatter
if _version_cartopy >= "0.18":
    FORMATTERS["dms"] = partial(pticker.DegreeFormatter, dms=True)
    FORMATTERS["dmslon"] = partial(pticker.LongitudeFormatter, dms=True)
    FORMATTERS["dmslat"] = partial(pticker.LatitudeFormatter, dms=True)

# Scale registry and presets
SCALES = mscale._scale_mapping
SCALES_PRESETS = {
    "quadratic": (
        "power",
        2,
    ),
    "cubic": (
        "power",
        3,
    ),
    "quartic": (
        "power",
        4,
    ),
    "height": ("exp", np.e, -1 / 7, 1013.25, True),
    "pressure": ("exp", np.e, -1 / 7, 1013.25, False),
    "db": ("exp", 10, 1, 0.1, True),
    "idb": ("exp", 10, 1, 0.1, False),
    "np": ("exp", np.e, 1, 1, True),
    "inp": ("exp", np.e, 1, 1, False),
}
mscale.register_scale(pscale.CutoffScale)
mscale.register_scale(pscale.ExpScale)
mscale.register_scale(pscale.FuncScale)
mscale.register_scale(pscale.InverseScale)
mscale.register_scale(pscale.LogScale)
mscale.register_scale(pscale.LinearScale)
mscale.register_scale(pscale.LogitScale)
mscale.register_scale(pscale.MercatorLatitudeScale)
mscale.register_scale(pscale.PowerScale)
mscale.register_scale(pscale.SineLatitudeScale)
mscale.register_scale(pscale.SymmetricalLogScale)

# Cartopy projection registry and basemap default keyword args
# NOTE: Normally basemap raises error if you omit keyword args
PROJ_DEFAULTS = {
    "geos": {"lon_0": 0},
    "eck4": {"lon_0": 0},
    "moll": {"lon_0": 0},
    "hammer": {"lon_0": 0},
    "kav7": {"lon_0": 0},
    "sinu": {"lon_0": 0},
    "vandg": {"lon_0": 0},
    "mbtfpq": {"lon_0": 0},
    "robin": {"lon_0": 0},
    "ortho": {"lon_0": 0, "lat_0": 0},
    "nsper": {"lon_0": 0, "lat_0": 0},
    "aea": {"lon_0": 0, "lat_0": 90, "width": 15000e3, "height": 15000e3},
    "eqdc": {"lon_0": 0, "lat_0": 90, "width": 15000e3, "height": 15000e3},
    "cass": {"lon_0": 0, "lat_0": 90, "width": 15000e3, "height": 15000e3},
    "gnom": {"lon_0": 0, "lat_0": 90, "width": 15000e3, "height": 15000e3},
    "poly": {"lon_0": 0, "lat_0": 0, "width": 10000e3, "height": 10000e3},
    "npaeqd": {"lon_0": 0, "boundinglat": 10},  # NOTE: everything breaks if you
    "nplaea": {"lon_0": 0, "boundinglat": 10},  # try to set boundinglat to zero
    "npstere": {"lon_0": 0, "boundinglat": 10},
    "spaeqd": {"lon_0": 0, "boundinglat": -10},
    "splaea": {"lon_0": 0, "boundinglat": -10},
    "spstere": {"lon_0": 0, "boundinglat": -10},
    "lcc": {
        "lon_0": 0,
        "lat_0": 40,
        "lat_1": 35,
        "lat_2": 45,  # use cartopy defaults
        "width": 20000e3,
        "height": 15000e3,
    },
    "tmerc": {"lon_0": 0, "lat_0": 0, "width": 10000e3, "height": 10000e3},
    "merc": {
        "llcrnrlat": -80,
        "urcrnrlat": 84,
        "llcrnrlon": -180,
        "urcrnrlon": 180,
    },
    "omerc": {
        "lat_0": 0,
        "lon_0": 0,
        "lat_1": -10,
        "lat_2": 10,
        "lon_1": 0,
        "lon_2": 0,
        "width": 10000e3,
        "height": 10000e3,
    },
}
if ccrs is None:
    PROJS = {}
else:
    PROJS = {
        "aitoff": pproj.Aitoff,
        "hammer": pproj.Hammer,
        "kav7": pproj.KavrayskiyVII,
        "wintri": pproj.WinkelTripel,
        "npgnom": pproj.NorthPolarGnomonic,
        "spgnom": pproj.SouthPolarGnomonic,
        "npaeqd": pproj.NorthPolarAzimuthalEquidistant,
        "spaeqd": pproj.SouthPolarAzimuthalEquidistant,
        "nplaea": pproj.NorthPolarLambertAzimuthalEqualArea,
        "splaea": pproj.SouthPolarLambertAzimuthalEqualArea,
    }
    PROJS_MISSING = {
        "aea": "AlbersEqualArea",
        "aeqd": "AzimuthalEquidistant",
        "cyl": "PlateCarree",  # only basemap name not matching PROJ
        "eck1": "EckertI",
        "eck2": "EckertII",
        "eck3": "EckertIII",
        "eck4": "EckertIV",
        "eck5": "EckertV",
        "eck6": "EckertVI",
        "eqc": "PlateCarree",  # actual PROJ name
        "eqdc": "EquidistantConic",
        "eqearth": "EqualEarth",  # better looking Robinson; not in basemap
        "euro": "EuroPP",  # Europe; not in basemap or PROJ
        "geos": "Geostationary",
        "gnom": "Gnomonic",
        "igh": "InterruptedGoodeHomolosine",  # not in basemap
        "laea": "LambertAzimuthalEqualArea",
        "lcc": "LambertConformal",
        "lcyl": "LambertCylindrical",  # not in basemap or PROJ
        "merc": "Mercator",
        "mill": "Miller",
        "moll": "Mollweide",
        "npstere": "NorthPolarStereo",  # np/sp stuff not in PROJ
        "nsper": "NearsidePerspective",
        "ortho": "Orthographic",
        "osgb": "OSGB",  # UK; not in basemap or PROJ
        "osni": "OSNI",  # Ireland; not in basemap or PROJ
        "pcarree": "PlateCarree",  # common alternate name
        "robin": "Robinson",
        "rotpole": "RotatedPole",
        "sinu": "Sinusoidal",
        "spstere": "SouthPolarStereo",
        "stere": "Stereographic",
        "tmerc": "TransverseMercator",
        "utm": "UTM",  # not in basemap
    }
    for _key, _cls in tuple(PROJS_MISSING.items()):
        if hasattr(ccrs, _cls):
            PROJS[_key] = getattr(ccrs, _cls)
            del PROJS_MISSING[_key]
    if PROJS_MISSING:
        warnings._warn_ultraplot(
            "The following cartopy projection(s) are unavailable: "
            + ", ".join(map(repr, PROJS_MISSING))
            + " . Please consider updating cartopy."
        )
    PROJS_TABLE = "The known cartopy projection classes are:\n" + "\n".join(
        " " + key + " " * (max(map(len, PROJS)) - len(key) + 10) + cls.__name__
        for key, cls in PROJS.items()
    )

# Geographic feature properties
FEATURES_CARTOPY = {  # positional arguments passed to NaturalEarthFeature
    "land": ("physical", "land"),
    "ocean": ("physical", "ocean"),
    "lakes": ("physical", "lakes"),
    "coast": ("physical", "coastline"),
    "rivers": ("physical", "rivers_lake_centerlines"),
    "borders": ("cultural", "admin_0_boundary_lines_land"),
    "innerborders": ("cultural", "admin_1_states_provinces_lakes"),
}
FEATURES_BASEMAP = {  # names of relevant basemap methods
    "land": "fillcontinents",
    "coast": "drawcoastlines",
    "rivers": "drawrivers",
    "borders": "drawcountries",
    "innerborders": "drawstates",
}

# Resolution names
# NOTE: Maximum basemap resolutions are much finer than cartopy
RESOS_CARTOPY = {
    "lo": "110m",
    "med": "50m",
    "hi": "10m",
    "x-hi": "10m",  # extra high
    "xx-hi": "10m",  # extra extra high
}
RESOS_BASEMAP = {
    "lo": "c",  # coarse
    "med": "l",
    "hi": "i",  # intermediate
    "x-hi": "h",
    "xx-hi": "f",  # fine
}


def _modify_colormap(cmap, *, cut, left, right, reverse, shift, alpha, samples):
    """
    Modify colormap using a variety of methods.
    """
    if cut is not None or left is not None or right is not None:
        if isinstance(cmap, pcolors.DiscreteColormap):
            if cut is not None:
                warnings._warn_ultraplot(
                    "Invalid argument 'cut' for ListedColormap. Ignoring."
                )
            cmap = cmap.truncate(left=left, right=right)
        else:
            cmap = cmap.cut(cut, left=left, right=right)
    if reverse:
        cmap = cmap.reversed()
    if shift is not None:
        cmap = cmap.shifted(shift)
    if alpha is not None:
        cmap = cmap.copy(alpha=alpha)
    if samples is not None:
        if isinstance(cmap, pcolors.DiscreteColormap):
            cmap = cmap.copy(N=samples)
        else:
            cmap = cmap.to_discrete(samples)
    return cmap


@warnings._rename_kwargs(
    "0.8.0", fade="saturation", shade="luminance", to_listed="discrete"
)
def Colormap(
    *args,
    name=None,
    listmode="perceptual",
    filemode="continuous",
    discrete=False,
    cycle=None,
    save=False,
    save_kw=None,
    **kwargs,
):
    """
    Generate, retrieve, modify, and/or merge instances of
    :class:`~ultraplot.colors.PerceptualColormap`,
    :class:`~ultraplot.colors.ContinuousColormap`, and
    :class:`~ultraplot.colors.DiscreteColormap`.

    Parameters
    ----------
    *args : colormap-spec
        Positional arguments that individually generate colormaps. If more
        than one argument is passed, the resulting colormaps are *merged* with
        `~ultraplot.colors.ContinuousColormap.append`
        or `~ultraplot.colors.DiscreteColormap.append`.
        The arguments are interpreted as follows:

        * If a registered colormap name, that colormap instance is looked up.
          If colormap instance is a native matplotlib colormap class, it is
          converted to a ultraplot colormap class.
        * If a filename string with valid extension, the colormap data
          is loaded with `ultraplot.colors.ContinuousColormap.from_file` or
          `ultraplot.colors.DiscreteColormap.from_file` depending on the value of
          `filemode` (see below). Default behavior is to load a
          :class:`~ultraplot.colors.ContinuousColormap`.
        * If RGB tuple or color string, a :class:`~ultraplot.colors.PerceptualColormap`
          is generated with `~ultraplot.colors.PerceptualColormap.from_color`.
          If the string ends in ``'_r'``, the monochromatic map will be
          *reversed*, i.e. will go from dark to light instead of light to dark.
        * If sequence of RGB tuples or color strings, a
          :class:`~ultraplot.colors.DiscreteColormap`, :class:`~ultraplot.colors.PerceptualColormap`,
          or :class:`~ultraplot.colors.ContinuousColormap` is generated depending on
          the value of `listmode` (see below). Default behavior is to generate a
          :class:`~ultraplot.colors.PerceptualColormap`.
        * If dictionary, a :class:`~ultraplot.colors.PerceptualColormap` is
          generated with `~ultraplot.colors.PerceptualColormap.from_hsl`.
          The dictionary should contain the keys ``'hue'``, ``'saturation'``,
          ``'luminance'``, and optionally ``'alpha'``, or their aliases (see below).

    name : str, optional
        Name under which the final colormap is registered. It can
        then be reused by passing ``cmap='name'`` to plotting
        functions. Names with leading underscores are ignored.
    filemode : {'perceptual', 'continuous', 'discrete'}, optional
        Controls how colormaps are generated when you input list(s) of colors.
        The options are as follows:

        * If ``'perceptual'`` or ``'continuous'``, a colormap is generated using
          `~ultraplot.colors.ContinuousColormap.from_file`. The resulting
          colormap may be a :class:`~ultraplot.colors.ContinuousColormap` or
          :class:`~ultraplot.colors.PerceptualColormap` depending on the data file.
        * If ``'discrete'``, a :class:`~ultraplot.colors.DiscreteColormap` is generated
          using `~ultraplot.colors.ContinuousColormap.from_file`.

        Default is ``'continuous'`` when calling `Colormap` directly and
        ``'discrete'`` when `Colormap` is called by `Cycle`.
    listmode : {'perceptual', 'continuous', 'discrete'}, optional
        Controls how colormaps are generated when you input sequence(s)
        of colors. The options are as follows:

        * If ``'perceptual'``, a :class:`~ultraplot.colors.PerceptualColormap`
          is generated with `~ultraplot.colors.PerceptualColormap.from_list`.
        * If ``'continuous'``, a :class:`~ultraplot.colors.ContinuousColormap` is
          generated with `~ultraplot.colors.ContinuousColormap.from_list`.
        * If ``'discrete'``, a :class:`~ultraplot.colors.DiscreteColormap` is generated
          by simply passing the colors to the class.

        Default is ``'perceptual'`` when calling `Colormap` directly and
        ``'discrete'`` when `Colormap` is called by `Cycle`.
    samples : int or sequence of int, optional
        For :class:`~ultraplot.colors.ContinuousColormap`\\ s, this is used to
        generate :class:`~ultraplot.colors.DiscreteColormap`\\ s with
        `~ultraplot.colors.ContinuousColormap.to_discrete`. For
        :class:`~ultraplot.colors.DiscreteColormap`\\ s, this is used to updates the
        number of colors in the cycle. If `samples` is integer, it applies
        to the final *merged* colormap. If it is a sequence of integers,
        it applies to each input colormap individually.
    discrete : bool, optional
        If ``True``, when the final colormap is a
        :class:`~ultraplot.colors.DiscreteColormap`, we leave it alone, but when it is a
        :class:`~ultraplot.colors.ContinuousColormap`, we always call
        `~ultraplot.colors.ContinuousColormap.to_discrete` with a
        default `samples` value of ``10``. This argument is not
        necessary if you provide the `samples` argument.
    left, right : float or sequence of float, optional
        Truncate the left or right edges of the colormap.
        Passed to :method:`~ultraplot.colors.ContinuousColormap.truncate`.
        If float, these apply to the final *merged* colormap. If sequence
        of float, these apply to each input colormap individually.
    cut : float or sequence of float, optional
        Cut out the center of the colormap. Passed to
        `~ultraplot.colors.ContinuousColormap.cut`. If float,
        this applies to the final *merged* colormap. If sequence of
        float, these apply to each input colormap individually.
    reverse : bool or sequence of bool, optional
        Reverse the colormap. Passed to
        `~ultraplot.colors.ContinuousColormap.reversed`. If
        float, this applies to the final *merged* colormap. If
        sequence of float, these apply to each input colormap individually.
    shift : float or sequence of float, optional
        Cyclically shift the colormap.
        Passed to :property:`~ultraplot.colors.ContinuousColormap.shifted`.
        If float, this applies to the final *merged* colormap. If sequence
        of float, these apply to each input colormap individually.
    a
        Shorthand for `alpha`.
    alpha : float or color-spec or sequence, optional
        The opacity of the colormap or the opacity gradation. Passed to
        `ultraplot.colors.ContinuousColormap.set_alpha`
        or `ultraplot.colors.DiscreteColormap.set_alpha`. If float, this applies
        to the final *merged* colormap. If sequence of float, these apply to
        each colormap individually.
    h, s, l, c
        Shorthands for `hue`, `luminance`, `saturation`, and `chroma`.
    hue, saturation, luminance : float or color-spec or sequence, optional
        The channel value(s) used to generate colormaps with
        `~ultraplot.colors.PerceptualColormap.from_hsl` and
        `~ultraplot.colors.PerceptualColormap.from_color`.

        * If you provided no positional arguments, these are used to create
          an arbitrary perceptually uniform colormap with
          `~ultraplot.colors.PerceptualColormap.from_hsl`. This
          is an alternative to passing a dictionary as a positional argument
          with `hue`, `saturation`, and `luminance` as dictionary keys (see `args`).
        * If you did provide positional arguments, and any of them are
          color specifications, these control the look of monochromatic colormaps
          generated with `~ultraplot.colors.PerceptualColormap.from_color`.
          To use different values for each colormap, pass a sequence of floats
          instead of a single float. Note the default `luminance` is ``90`` if
          `discrete` is ``True`` and ``100`` otherwise.

    chroma
        Alias for `saturation`.
    cycle : str, optional
        The registered cycle name used to interpret color strings like ``'C0'``
        and ``'C2'``. Default is from the active property :rcraw:`cycle`. This lets
        you make monochromatic colormaps using colors selected from arbitrary cycles.
    save : bool, optional
        Whether to call the colormap/color cycle save method, i.e.
        `ultraplot.colors.ContinuousColormap.save` or
        `ultraplot.colors.DiscreteColormap.save`.
    save_kw : dict-like, optional
        Ignored if `save` is ``False``. Passed to the colormap/color cycle
        save method, i.e. `ultraplot.colors.ContinuousColormap.save` or
        `ultraplot.colors.DiscreteColormap.save`.

    Other parameters
    ----------------
    **kwargs
        Passed to `ultraplot.colors.ContinuousColormap.copy`,
        `ultraplot.colors.PerceptualColormap.copy`, or
        `ultraplot.colors.DiscreteColormap.copy`.

    Returns
    -------
    matplotlib.colors.Colormap
        A :class:`~ultraplot.colors.ContinuousColormap` or
        :class:`~ultraplot.colors.DiscreteColormap` instance.

    See also
    --------
    matplotlib.colors.Colormap
    matplotlib.colors.LinearSegmentedColormap
    matplotlib.colors.ListedColormap
    ultraplot.constructor.Norm
    ultraplot.constructor.Cycle
    ultraplot.utils.get_colors
    """

    # Helper function
    # NOTE: Very careful here! Try to support common use cases. For example
    # adding opacity gradations to colormaps with Colormap('cmap', alpha=(0.5, 1))
    # or sampling maps with Colormap('cmap', samples=np.linspace(0, 1, 11)) should
    # be allowable.
    # If *args is singleton try to preserve it.
    def _pop_modification(key):
        value = kwargs.pop(key, None)
        if not np.iterable(value) or isinstance(value, str):
            values = (None,) * len(args)
        elif len(args) == len(value):
            values, value = tuple(value), None
        elif len(args) == 1:  # e.g. Colormap('cmap', alpha=(0.5, 1))
            values = (None,)
        else:
            raise ValueError(
                f"Got {len(args)} colormap-specs "
                f"but {len(value)} values for {key!r}."
            )
        return value, values

    # Parse keyword args that can apply to the merged colormap or each one
    hsla = _pop_props(kwargs, "hsla")
    if not args and hsla.keys() - {"alpha"}:
        args = (hsla,)
    else:
        kwargs.update(hsla)
    default_luminance = kwargs.pop("default_luminance", None)  # used internally
    cut, cuts = _pop_modification("cut")
    left, lefts = _pop_modification("left")
    right, rights = _pop_modification("right")
    shift, shifts = _pop_modification("shift")
    reverse, reverses = _pop_modification("reverse")
    samples, sampless = _pop_modification("samples")
    alpha, alphas = _pop_modification("alpha")
    luminance, luminances = _pop_modification("luminance")
    saturation, saturations = _pop_modification("saturation")
    if luminance is not None:
        luminances = (luminance,) * len(args)
    if saturation is not None:
        saturations = (saturation,) * len(args)

    # Issue warnings and errors
    if not args:
        raise ValueError(
            "Colormap() requires either positional arguments or "
            "'hue', 'chroma', 'saturation', and/or 'luminance' keywords."
        )
    deprecated = {"listed": "discrete", "linear": "continuous"}
    if listmode in deprecated:
        oldmode, listmode = listmode, deprecated[listmode]
        warnings._warn_ultraplot(
            f"Please use listmode={listmode!r} instead of listmode={oldmode!r}."
            "Option was renamed in v0.8 and will be removed in a future relase."
        )
    options = {"discrete", "continuous", "perceptual"}
    for key, mode in zip(("listmode", "filemode"), (listmode, filemode)):
        if mode not in options:
            raise ValueError(
                f"Invalid {key}={mode!r}. Options are: "
                + ", ".join(map(repr, options))
                + "."
            )

    # Loop through colormaps
    cmaps = []
    for (
        arg,
        icut,
        ileft,
        iright,
        ireverse,
        ishift,
        isamples,
        iluminance,
        isaturation,
        ialpha,
    ) in zip(  # noqa: E501
        args,
        cuts,
        lefts,
        rights,
        reverses,
        shifts,
        sampless,
        luminances,
        saturations,
        alphas,  # noqa: E501
    ):
        # Load registered colormaps and maps on file
        # TODO: Document how 'listmode' also affects loaded files
        if isinstance(arg, str):
            if "." in arg and os.path.isfile(arg):
                if filemode == "discrete":
                    arg = pcolors.DiscreteColormap.from_file(arg)
                else:
                    arg = pcolors.ContinuousColormap.from_file(arg)
            else:
                # FIXME: This error is baffling too me. Colors and colormaps
                # are used interchangeable here
                try:
                    arg = pcolors._cmap_database.get_cmap(arg)
                except KeyError:
                    pass

        # Convert matplotlib colormaps to subclasses
        if isinstance(arg, mcolors.Colormap):
            cmap = pcolors._translate_cmap(arg)

        # Dictionary of hue/sat/luminance values or 2-tuples
        elif isinstance(arg, dict):
            cmap = pcolors.PerceptualColormap.from_hsl(**arg)

        # List of color tuples or color strings, i.e. iterable of iterables
        elif (
            not isinstance(arg, str)
            and np.iterable(arg)
            and all(np.iterable(color) for color in arg)
        ):
            if listmode == "discrete":
                cmap = pcolors.DiscreteColormap(arg)
            elif listmode == "continuous":
                cmap = pcolors.ContinuousColormap.from_list(arg)
            else:
                cmap = pcolors.PerceptualColormap.from_list(arg)

        # Monochrome colormap from input color
        # NOTE: Do not print color names in error message. Too long to be useful.
        else:
            jreverse = isinstance(arg, str) and arg[-2:] == "_r"
            if jreverse:
                arg = arg[:-2]
            try:
                color = to_rgba(arg, cycle=cycle)
            except (ValueError, TypeError):
                message = f"Invalid colormap, color cycle, or color {arg!r}."
                if isinstance(arg, str) and arg[:1] != "#":
                    message += (
                        " Options include: "
                        + ", ".join(sorted(map(repr, pcolors._cmap_database)))
                        + "."
                    )
                raise ValueError(message) from None
            iluminance = _not_none(iluminance, default_luminance)
            cmap = pcolors.PerceptualColormap.from_color(
                color, luminance=iluminance, saturation=isaturation
            )
            ireverse = _not_none(ireverse, False)
            ireverse = ireverse ^ jreverse  # xor

        # Modify the colormap
        cmap = _modify_colormap(
            cmap,
            cut=icut,
            left=ileft,
            right=iright,
            reverse=ireverse,
            shift=ishift,
            alpha=ialpha,
            samples=isamples,
        )
        cmaps.append(cmap)

    # Merge the resulting colormaps
    if len(cmaps) > 1:  # more than one map and modify arbitrary properties
        cmap = cmaps[0].append(*cmaps[1:], **kwargs)
    else:
        cmap = cmaps[0].copy(**kwargs)

    # Modify the colormap
    if discrete and isinstance(cmap, pcolors.ContinuousColormap):  # noqa: E501
        samples = _not_none(samples, DEFAULT_CYCLE_SAMPLES)
    cmap = _modify_colormap(
        cmap,
        cut=cut,
        left=left,
        right=right,
        reverse=reverse,
        shift=shift,
        alpha=alpha,
        samples=samples,
    )

    # Initialize
    if not cmap._isinit:
        cmap._init()

    # Register the colormap
    if name is None:
        name = cmap.name  # may have been modified by e.g. reversed()
    else:
        cmap.name = name
    if not isinstance(name, str):
        raise ValueError("The colormap name must be a string.")
    pcolors._cmap_database.register(cmap, name=name)

    # Save the colormap
    if save:
        save_kw = save_kw or {}
        cmap.save(**save_kw)

    return cmap


class Cycle(cycler.Cycler):
    """
    Generate and merge `~cycler.Cycler` instances in a variety of ways. The new generated class can be used to internally map keywords to the properties of the `~cycler.Cycler` instance. It is used by various plot functions to cycle through colors, linestyles, markers, etc.

    Parameters
    ----------
    *args : colormap-spec or cycle-spec, optional
        Positional arguments control the *colors* in the `~cycler.Cycler`
        object. If zero arguments are passed, the single color ``'black'``
        is used. If more than one argument is passed, the resulting cycles
        are merged. Arguments are interpreted as follows:

        * If a `~cycler.Cycler`, nothing more is done.
        * If a sequence of RGB tuples or color strings, these colors are used.
        * If a :class:`~ultraplot.colors.DiscreteColormap`, colors from the ``colors``
        attribute are used.
        * If a string cycle name, that :class:`~ultraplot.colors.DiscreteColormap`
        is looked up and its ``colors`` are used.
        * In all other cases, the argument is passed to `Colormap`, and
        colors from the resulting :class:`~ultraplot.colors.ContinuousColormap`
        are used. See the `samples` argument.

        If the last positional argument is numeric, it is used for the
        `samples` keyword argument.
    N
        Shorthand for `samples`.
    samples : float or sequence of float, optional
        For :class:`~ultraplot.colors.DiscreteColormap`\\ s, this is the number of
        colors to select. For example, ``Cycle('538', 4)`` returns the first 4
        colors of the ``'538'`` color cycle.
        For :class:`~ultraplot.colors.ContinuousColormap`\\ s, this is either a
        sequence of sample coordinates used to draw colors from the colormap, or
        an integer number of colors to draw. If the latter, the sample coordinates
        are ``np.linspace(0, 1, samples)``. For example, ``Cycle('Reds', 5)``
        divides the ``'Reds'`` colormap into five evenly spaced colors.

    Other parameters
    ----------------
    c, color, colors : sequence of color-spec, optional
        A sequence of colors passed as keyword arguments. This is equivalent
        to passing a sequence of colors as the first positional argument and is
        included for consistency with `~matplotlib.axes.Axes.set_prop_cycle`.
        If positional arguments were passed, the colors in this list are
        appended to the colors resulting from the positional arguments.
    lw, ls, d, a, m, ms, mew, mec, mfc
        Shorthands for the below keywords.
    linewidth, linestyle, dashes, alpha, marker, markersize, markeredgewidth, \
markeredgecolor, markerfacecolor : object or sequence of object, optional
        Lists of `~matplotlib.lines.Line2D` properties that can be added to the
        `~cycler.Cycler` instance. If the input was already a `~cycler.Cycler`,
        these are added or appended to the existing cycle keys. If the lists have
        unequal length, they are repeated to their least common multiple (unlike
        `~cycler.cycler`, which throws an error in this case). For more info
        on cyclers see `~matplotlib.axes.Axes.set_prop_cycle`. Also see
        the `line style reference \
<https://matplotlib.org/2.2.5/gallery/lines_bars_and_markers/line_styles_reference.html>`__,
        the `marker reference \
<https://matplotlib.org/stable/gallery/lines_bars_and_markers/marker_reference.html>`__,
        and the `custom dashes reference \
<https://matplotlib.org/stable/gallery/lines_bars_and_markers/line_demo_dash_control.html>`__.
    linewidths, linestyles, dashes, alphas, markers, markersizes, markeredgewidths, \
markeredgecolors, markerfacecolors
        Aliases for the above keywords.
    **kwargs
        If the input is not already a `~cycler.Cycler` instance, these are passed
        to `Colormap` and used to build the :class:`~ultraplot.colors.DiscreteColormap`
        from which the cycler will draw its colors.

    See also
    --------
    cycler.cycler
    cycler.Cycler
    matplotlib.axes.Axes.set_prop_cycle
    ultraplot.constructor.Colormap
    ultraplot.constructor.Norm
    ultraplot.utils.get_colors
    """

    def __init__(self, *args, N=None, samples=None, name=None, **kwargs):
        cycler_props = self._parse_basic_properties(kwargs)
        samples = _not_none(samples=samples, N=N)  # trigger Colormap default
        if not args:
            self._handle_empty_args(cycler_props, kwargs)
        elif self._is_all_cyclers(args):
            self._handle_cycler_args(args, cycler_props, kwargs)
        else:
            self._handle_colormap_args(args, cycler_props, kwargs, samples, name)

        self._iterator = None  # internal reference for cycle
        self.name = _not_none(name, "_no_name")

    def _parse_basic_properties(self, kwargs):
        """Parse and validate basic properties from kwargs."""
        props = _pop_props(kwargs, "line")
        if "sizes" in kwargs:
            props.setdefault("markersize", kwargs.pop("sizes"))

        for key, value in tuple(props.items()):
            if value is None:
                props[key] = ["black"]  # default instead of early return
            elif not np.iterable(value) or isinstance(value, str):
                props[key] = [value]
            else:
                props[key] = list(value)  # ensure mutable list
        return props

    def _handle_empty_args(self, props, kwargs):
        """Handle case when no positional arguments are provided."""
        props.setdefault("color", ["black"])
        if kwargs:
            warnings._warn_ultraplot(f"Ignoring Cycle() keyword arg(s) {kwargs}.")
        self._build_cycler((props,))

    def _handle_cycler_args(self, args, props, kwargs):
        """Handle case when arguments are cycler objects."""
        if kwargs:
            warnings._warn_ultraplot(f"Ignoring Cycle() keyword arg(s) {kwargs}.")
        if len(args) == 1 and not props:
            self._build_cycler((args[0].by_key(),))
        else:
            dicts = tuple(arg.by_key() for arg in args)
            self._build_cycler(dicts + (props,))

    def _handle_colormap_args(self, args, props, kwargs, samples, name):
        """Handle case when arguments are for creating a colormap."""
        if isinstance(args[-1], Number):
            args, samples = args[:-1], _not_none(
                samples_positional=args[-1], samples=samples
            )

        cmap = self._create_colormap(args, name, samples, kwargs)
        dict_ = {"color": [c if isinstance(c, str) else to_hex(c) for c in cmap.colors]}
        self._build_cycler((dict_, props))
        self.name = _not_none(name, cmap.name)

    def _create_colormap(self, args, name, samples, kwargs):
        """Create a colormap from the given arguments."""
        kwargs.setdefault("listmode", "discrete")
        kwargs.setdefault("filemode", "discrete")
        kwargs["discrete"] = True
        kwargs["default_luminance"] = DEFAULT_CYCLE_LUMINANCE
        return Colormap(*args, name=name, samples=samples, **kwargs)

    def _is_all_cyclers(self, args):
        """Check if all arguments are Cycler objects."""
        return all(isinstance(arg, cycler.Cycler) for arg in args)

    def _build_cycler(self, dicts):
        """Build the final cycler from the given dictionaries."""
        props = {}
        for dict_ in dicts:
            for key, value in dict_.items():
                props.setdefault(key, []).extend(value)
        # Build cycler with matching property lengths
        # Ensure at least a default color property exists
        # Build cycler with matching property lengths
        lengths = [len(value) for value in props.values()]
        maxlen = np.lcm.reduce(lengths)
        props = {
            key: value * (maxlen // len(value))
            for key, value in props.items()
            if len(value)
        }
        # Set default color property if not present
        if "color" not in props or not props:
            props = {"color": ["black"]}
        mcycler = cycler.cycler(**props)
        super().__init__(mcycler)

    def __eq__(self, other):
        for a, b in zip(self, other):
            if a != b:
                return False
        return True

    def get_next(self):
        # Get the next set of properties
        if self._iterator is None:
            self._iterator = iter(self)
        try:
            return next(self._iterator)
        except StopIteration:
            self._iterator = iter(self)
            return next(self._iterator)


def Norm(norm, *args, **kwargs):
    """
    Return an arbitrary `~matplotlib.colors.Normalize` instance. See this
    `tutorial <https://matplotlib.org/stable/tutorials/colors/colormapnorms.html>`__
    for an introduction to matplotlib normalizers.

    Parameters
    ----------
    norm : str or `~matplotlib.colors.Normalize`
        The normalizer specification. If a `~matplotlib.colors.Normalize`
        instance already, a `copy.copy` of the instance is returned.
        Otherwise, `norm` should be a string corresponding to one of
        the "registered" colormap normalizers (see below table).

        If `norm` is a list or tuple and the first element is a "registered"
        normalizer name, subsequent elements are passed to the normalizer class
        as positional arguments.

        .. _norm_table:

        ===============================  =====================================
        Key(s)                           Class
        ===============================  =====================================
        ``'null'``, ``'none'``           `~matplotlib.colors.NoNorm`
        ``'diverging'``, ``'div'``       `~ultraplot.colors.DivergingNorm`
        ``'segmented'``, ``'segments'``  `~ultraplot.colors.SegmentedNorm`
        ``'linear'``                     `~matplotlib.colors.Normalize`
        ``'log'``                        `~matplotlib.colors.LogNorm`
        ``'power'``                      `~matplotlib.colors.PowerNorm`
        ``'symlog'``                     `~matplotlib.colors.SymLogNorm`
        ===============================  =====================================

    Other parameters
    ----------------
    *args, **kwargs
        Passed to the `~matplotlib.colors.Normalize` initializer.

    Returns
    -------
    matplotlib.colors.Normalize
        A `~matplotlib.colors.Normalize` instance.

    See also
    --------
    matplotlib.colors.Normalize
    ultraplot.colors.DiscreteNorm
    ultraplot.constructor.Colormap
    """
    if np.iterable(norm) and not isinstance(norm, str):
        norm, *args = *norm, *args
    if isinstance(norm, mcolors.Normalize):
        return copy.copy(norm)
    if not isinstance(norm, str):
        raise ValueError(f"Invalid norm name {norm!r}. Must be string.")
    if norm not in NORMS:
        raise ValueError(
            f"Unknown normalizer {norm!r}. Options are: "
            + ", ".join(map(repr, NORMS))
            + "."
        )
    if norm == "symlog" and not args and "linthresh" not in kwargs:
        kwargs["linthresh"] = 1  # special case, needs argument
    return NORMS[norm](*args, **kwargs)


def Locator(locator, *args, discrete=False, **kwargs):
    """
    Return a `~matplotlib.ticker.Locator` instance.

    Parameters
    ----------
    locator : `~matplotlib.ticker.Locator`, str, bool, float, or sequence
        The locator specification, interpreted as follows:

        * If a `~matplotlib.ticker.Locator` instance already,
          a `copy.copy` of the instance is returned.
        * If ``False``, a `~matplotlib.ticker.NullLocator` is used, and if
          ``True``, the default `~matplotlib.ticker.AutoLocator` is used.
        * If a number, this specifies the *step size* between tick locations.
          Returns a `~matplotlib.ticker.MultipleLocator`.
        * If a sequence of numbers, these points are ticked. Returns
          a `~matplotlib.ticker.FixedLocator` by default or a
          `~ultraplot.ticker.DiscreteLocator` if `discrete` is ``True``.

        Otherwise, `locator` should be a string corresponding to one
        of the "registered" locators (see below table). If `locator` is a
        list or tuple and the first element is a "registered" locator name,
        subsequent elements are passed to the locator class as positional
        arguments. For example, ``uplt.Locator(('multiple', 5))`` is
        equivalent to ``uplt.Locator('multiple', 5)``.

        .. _locator_table:

        =======================  ============================================  =====================================================================================
        Key                      Class                                         Description
        =======================  ============================================  =====================================================================================
        ``'null'``, ``'none'``   `~matplotlib.ticker.NullLocator`              No ticks
        ``'auto'``               `~matplotlib.ticker.AutoLocator`              Major ticks at sensible locations
        ``'minor'``              `~matplotlib.ticker.AutoMinorLocator`         Minor ticks at sensible locations
        ``'date'``               `~matplotlib.dates.AutoDateLocator`           Default tick locations for datetime axes
        ``'fixed'``              `~matplotlib.ticker.FixedLocator`             Ticks at these exact locations
        ``'discrete'``           `~ultraplot.ticker.DiscreteLocator`             Major ticks restricted to these locations but subsampled depending on the axis length
        ``'discreteminor'``      `~ultraplot.ticker.DiscreteLocator`             Minor ticks restricted to these locations but subsampled depending on the axis length
        ``'index'``              :class:`~ultraplot.ticker.IndexLocator`                Ticks on the non-negative integers
        ``'linear'``             `~matplotlib.ticker.LinearLocator`            Exactly ``N`` ticks encompassing axis limits, spaced as ``numpy.linspace(lo, hi, N)``
        ``'log'``                `~matplotlib.ticker.LogLocator`               For log-scale axes
        ``'logminor'``           `~matplotlib.ticker.LogLocator`               For log-scale axes on the 1st through 9th multiples of each power of the base
        ``'logit'``              `~matplotlib.ticker.LogitLocator`             For logit-scale axes
        ``'logitminor'``         `~matplotlib.ticker.LogitLocator`             For logit-scale axes with ``minor=True`` passed to `~matplotlib.ticker.LogitLocator`
        ``'maxn'``               `~matplotlib.ticker.MaxNLocator`              No more than ``N`` ticks at sensible locations
        ``'multiple'``           `~matplotlib.ticker.MultipleLocator`          Ticks every ``N`` step away from zero
        ``'symlog'``             `~matplotlib.ticker.SymmetricalLogLocator`    For symlog-scale axes
        ``'symlogminor'``        `~matplotlib.ticker.SymmetricalLogLocator`    For symlog-scale axes on the 1st through 9th multiples of each power of the base
        ``'theta'``              `~matplotlib.projections.polar.ThetaLocator`  Like the base locator but default locations are every `numpy.pi` / 8 radians
        ``'year'``               `~matplotlib.dates.YearLocator`               Ticks every ``N`` years
        ``'month'``              `~matplotlib.dates.MonthLocator`              Ticks every ``N`` months
        ``'weekday'``            `~matplotlib.dates.WeekdayLocator`            Ticks every ``N`` weekdays
        ``'day'``                `~matplotlib.dates.DayLocator`                Ticks every ``N`` days
        ``'hour'``               `~matplotlib.dates.HourLocator`               Ticks every ``N`` hours
        ``'minute'``             `~matplotlib.dates.MinuteLocator`             Ticks every ``N`` minutes
        ``'second'``             `~matplotlib.dates.SecondLocator`             Ticks every ``N`` seconds
        ``'microsecond'``        `~matplotlib.dates.MicrosecondLocator`        Ticks every ``N`` microseconds
        ``'lon'``, ``'deglon'``  `~ultraplot.ticker.LongitudeLocator`            Longitude gridlines at sensible decimal locations
        ``'lat'``, ``'deglat'``  `~ultraplot.ticker.LatitudeLocator`             Latitude gridlines at sensible decimal locations
        ``'dms'``                `~ultraplot.ticker.DegreeLocator`               Gridlines on nice minute and second intervals
        ``'dmslon'``             `~ultraplot.ticker.LongitudeLocator`            Longitude gridlines on nice minute and second intervals
        ``'dmslat'``             `~ultraplot.ticker.LatitudeLocator`             Latitude gridlines on nice minute and second intervals
        =======================  ============================================  =====================================================================================

    Other parameters
    ----------------
    *args, **kwargs
        Passed to the `~matplotlib.ticker.Locator` class.

    Returns
    -------
    matplotlib.ticker.Locator
        A `~matplotlib.ticker.Locator` instance.

    See also
    --------
    matplotlib.ticker.Locator
    ultraplot.axes.CartesianAxes.format
    ultraplot.axes.PolarAxes.format
    ultraplot.axes.GeoAxes.format
    ultraplot.axes.Axes.colorbar
    ultraplot.constructor.Formatter
    """  # noqa: E501

    if (
        np.iterable(locator)
        and not isinstance(locator, str)
        and not all(isinstance(num, Number) for num in locator)
    ):
        locator, *args = *locator, *args
    if isinstance(locator, mticker.Locator):
        return copy.copy(locator)
    if isinstance(locator, str):
        if locator == "index":  # defaults
            args = args or (1,)
            if len(args) == 1:
                args = (*args, 0)
        elif locator in ("logminor", "logitminor", "symlogminor"):  # presets
            locator, _ = locator.split("minor")
            if locator == "logit":
                kwargs.setdefault("minor", True)
            else:
                kwargs.setdefault("subs", np.arange(1, 10))
        if locator in LOCATORS:
            locator = LOCATORS[locator](*args, **kwargs)
        else:
            raise ValueError(
                f"Unknown locator {locator!r}. Options are: "
                + ", ".join(map(repr, LOCATORS))
                + "."
            )
    elif locator is True:
        locator = mticker.AutoLocator(*args, **kwargs)
    elif locator is False:
        locator = mticker.NullLocator(*args, **kwargs)
    elif isinstance(locator, Number):  # scalar variable
        locator = mticker.MultipleLocator(locator, *args, **kwargs)
    elif np.iterable(locator):
        locator = np.array(locator)
        if discrete:
            locator = pticker.DiscreteLocator(locator, *args, **kwargs)
        else:
            locator = mticker.FixedLocator(locator, *args, **kwargs)
    else:
        raise ValueError(f"Invalid locator {locator!r}.")
    return locator


def Formatter(formatter, *args, date=False, index=False, **kwargs):
    """
    Return a `~matplotlib.ticker.Formatter` instance.

    Parameters
    ----------
    formatter : `~matplotlib.ticker.Formatter`, str, bool, callable, or sequence
        The formatter specification, interpreted as follows:

        * If a `~matplotlib.ticker.Formatter` instance already,
          a `copy.copy` of the instance is returned.
        * If ``False``, a `~matplotlib.ticker.NullFormatter` is used, and if
          ``True``, the default `~ultraplot.ticker.AutoFormatter` is used.
        * If a function, the labels will be generated using this function.
          Returns a `~matplotlib.ticker.FuncFormatter`.
        * If sequence of strings, the ticks are labeled with these strings.
          Returns a `~matplotlib.ticker.FixedFormatter` by default or
          an :class:`~ultraplot.ticker.IndexFormatter` if `index` is ``True``.
        * If a string containing ``{x}`` or ``{x:...}``, ticks will be
          formatted by calling ``string.format(x=number)``. Returns
          a `~matplotlib.ticker.StrMethodFormatter`.
        * If a string containing ``'%'`` and `date` is ``False``, ticks
          will be formatted using the C-style ``string % number`` method. See
          `this page <https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting>`__
          for a review. Returns a `~matplotlib.ticker.FormatStrFormatter`.
        * If a string containing ``'%'`` and `date` is ``True``, ticks
          will be formatted using `~datetime.datetime.strfrtime`. See
          `this page <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`__
          for a review. Returns a `~matplotlib.dates.DateFormatter`.

        Otherwise, `formatter` should be a string corresponding to one of the
        "registered" formatters or formatter presets (see below table). If
        `formatter` is a list or tuple and the first element is a "registered"
        formatter name, subsequent elements are passed to the formatter class
        as positional arguments. For example, ``uplt.Formatter(('sigfig', 3))`` is
        equivalent to ``Formatter('sigfig', 3)``.


        .. _tau: https://tauday.com/tau-manifesto

        .. _formatter_table:

        ======================  ==============================================  =================================================================
        Key                     Class                                           Description
        ======================  ==============================================  =================================================================
        ``'null'``, ``'none'``  `~matplotlib.ticker.NullFormatter`              No tick labels
        ``'auto'``              `~ultraplot.ticker.AutoFormatter`                 New default tick labels for axes
        ``'sci'``               `~ultraplot.ticker.SciFormatter`                  Format ticks with scientific notation
        ``'simple'``            `~ultraplot.ticker.SimpleFormatter`               New default tick labels for e.g. contour labels
        ``'sigfig'``            `~ultraplot.ticker.SigFigFormatter`               Format labels using the first ``N`` significant digits
        ``'frac'``              `~ultraplot.ticker.FracFormatter`                 Rational fractions
        ``'date'``              `~matplotlib.dates.AutoDateFormatter`           Default tick labels for datetime axes
        ``'concise'``           `~matplotlib.dates.ConciseDateFormatter`        More concise date labels introduced in matplotlib 3.1
        ``'datestr'``           `~matplotlib.dates.DateFormatter`               Date formatting with C-style ``string % format`` notation
        ``'eng'``               `~matplotlib.ticker.EngFormatter`               Engineering notation
        ``'fixed'``             `~matplotlib.ticker.FixedFormatter`             List of strings
        ``'formatstr'``         `~matplotlib.ticker.FormatStrFormatter`         From C-style ``string % format`` notation
        ``'func'``              `~matplotlib.ticker.FuncFormatter`              Use an arbitrary function
        ``'index'``             :class:`~ultraplot.ticker.IndexFormatter`                List of strings corresponding to non-negative integer positions
        ``'log'``               `~matplotlib.ticker.LogFormatterSciNotation`    For log-scale axes with scientific notation
        ``'logit'``             `~matplotlib.ticker.LogitFormatter`             For logistic-scale axes
        ``'percent'``           `~matplotlib.ticker.PercentFormatter`           Trailing percent sign
        ``'scalar'``            `~matplotlib.ticker.ScalarFormatter`            The default matplotlib formatter
        ``'strmethod'``         `~matplotlib.ticker.StrMethodFormatter`         From the ``string.format`` method
        ``'theta'``             `~matplotlib.projections.polar.ThetaFormatter`  Formats radians as degrees, with a degree symbol
        ``'e'``                 `~ultraplot.ticker.FracFormatter` preset          Fractions of *e*
        ``'pi'``                `~ultraplot.ticker.FracFormatter` preset          Fractions of :math:`\\pi`
        ``'tau'``               `~ultraplot.ticker.FracFormatter` preset          Fractions of the `one true circle constant <tau_>`_ :math:`\\tau`
        ``'lat'``               `~ultraplot.ticker.AutoFormatter` preset          Cardinal "SN" indicator
        ``'lon'``               `~ultraplot.ticker.AutoFormatter` preset          Cardinal "WE" indicator
        ``'deg'``               `~ultraplot.ticker.AutoFormatter` preset          Trailing degree symbol
        ``'deglat'``            `~ultraplot.ticker.AutoFormatter` preset          Trailing degree symbol and cardinal "SN" indicator
        ``'deglon'``            `~ultraplot.ticker.AutoFormatter` preset          Trailing degree symbol and cardinal "WE" indicator
        ``'dms'``               `~ultraplot.ticker.DegreeFormatter`               Labels with degree/minute/second support
        ``'dmslon'``            `~ultraplot.ticker.LongitudeFormatter`            Longitude labels with degree/minute/second support
        ``'dmslat'``            `~ultraplot.ticker.LatitudeFormatter`             Latitude labels with degree/minute/second support
        ======================  ==============================================  =================================================================

    date : bool, optional
        Toggles the behavior when `formatter` contains a ``'%'`` sign
        (see above).
    index : bool, optional
        Controls the behavior when `formatter` is a sequence of strings
        (see above).

    Other parameters
    ----------------
    *args, **kwargs
        Passed to the `~matplotlib.ticker.Formatter` class.

    Returns
    -------
    matplotlib.ticker.Formatter
        A `~matplotlib.ticker.Formatter` instance.

    See also
    --------
    matplotlib.ticker.Formatter
    ultraplot.axes.CartesianAxes.format
    ultraplot.axes.PolarAxes.format
    ultraplot.axes.GeoAxes.format
    ultraplot.axes.Axes.colorbar
    ultraplot.constructor.Locator
    """  # noqa: E501
    if (
        np.iterable(formatter)
        and not isinstance(formatter, str)
        and not all(isinstance(item, str) for item in formatter)
    ):
        formatter, *args = *formatter, *args
    if isinstance(formatter, mticker.Formatter):
        return copy.copy(formatter)
    if isinstance(formatter, str):
        if re.search(r"{x(:.+)?}", formatter):  # str.format
            formatter = mticker.StrMethodFormatter(formatter, *args, **kwargs)
        elif "%" in formatter:  # str % format
            cls = mdates.DateFormatter if date else mticker.FormatStrFormatter
            formatter = cls(formatter, *args, **kwargs)
        elif formatter in FORMATTERS:
            formatter = FORMATTERS[formatter](*args, **kwargs)
        else:
            raise ValueError(
                f"Unknown formatter {formatter!r}. Options are: "
                + ", ".join(map(repr, FORMATTERS))
                + "."
            )
    elif formatter is True:
        formatter = pticker.AutoFormatter(*args, **kwargs)
    elif formatter is False:
        formatter = mticker.NullFormatter(*args, **kwargs)
    elif np.iterable(formatter):
        formatter = (mticker.FixedFormatter, pticker.IndexFormatter)[index](formatter)
    elif callable(formatter):
        formatter = mticker.FuncFormatter(formatter, *args, **kwargs)
    else:
        raise ValueError(f"Invalid formatter {formatter!r}.")
    return formatter


def Scale(scale, *args, **kwargs):
    """
    Return a `~matplotlib.scale.ScaleBase` instance.

    Parameters
    ----------
    scale : `~matplotlib.scale.ScaleBase`, str, or tuple
        The axis scale specification. If a `~matplotlib.scale.ScaleBase` instance
        already, a `copy.copy` of the instance is returned. Otherwise, `scale`
        should be a string corresponding to one of the "registered" axis scales
        or axis scale presets (see below table).

        If `scale` is a list or tuple and the first element is a
        "registered" scale name, subsequent elements are passed to the
        scale class as positional arguments.

        .. _scale_table:

        =================  ======================================  ===============================================
        Key                Class                                   Description
        =================  ======================================  ===============================================
        ``'linear'``       `~ultraplot.scale.LinearScale`            Linear
        ``'log'``          `~ultraplot.scale.LogScale`               Logarithmic
        ``'symlog'``       `~ultraplot.scale.SymmetricalLogScale`    Logarithmic beyond finite space around zero
        ``'logit'``        `~ultraplot.scale.LogitScale`             Logistic
        ``'inverse'``      `~ultraplot.scale.InverseScale`           Inverse
        ``'function'``     `~ultraplot.scale.FuncScale`              Arbitrary forward and backwards transformations
        ``'sine'``         `~ultraplot.scale.SineLatitudeScale`      Sine function (in degrees)
        ``'mercator'``     `~ultraplot.scale.MercatorLatitudeScale`  Mercator latitude function (in degrees)
        ``'exp'``          `~ultraplot.scale.ExpScale`               Arbitrary exponential function
        ``'power'``        `~ultraplot.scale.PowerScale`             Arbitrary power function
        ``'cutoff'``       `~ultraplot.scale.CutoffScale`            Arbitrary piecewise linear transformations
        ``'quadratic'``    `~ultraplot.scale.PowerScale` (preset)    Quadratic function
        ``'cubic'``        `~ultraplot.scale.PowerScale` (preset)    Cubic function
        ``'quartic'``      `~ultraplot.scale.PowerScale` (preset)    Quartic function
        ``'db'``           `~ultraplot.scale.ExpScale` (preset)      Ratio expressed as `decibels <db_>`_
        ``'np'``           `~ultraplot.scale.ExpScale` (preset)      Ratio expressed as `nepers <np_>`_
        ``'idb'``          `~ultraplot.scale.ExpScale` (preset)      `Decibels <db_>`_ expressed as ratio
        ``'inp'``          `~ultraplot.scale.ExpScale` (preset)      `Nepers <np_>`_ expressed as ratio
        ``'pressure'``     `~ultraplot.scale.ExpScale` (preset)      Height (in km) expressed linear in pressure
        ``'height'``       `~ultraplot.scale.ExpScale` (preset)      Pressure (in hPa) expressed linear in height
        =================  ======================================  ===============================================

        .. _db: https://en.wikipedia.org/wiki/Decibel
        .. _np: https://en.wikipedia.org/wiki/Neper

    Other parameters
    ----------------
    *args, **kwargs
        Passed to the `~matplotlib.scale.ScaleBase` class.

    Returns
    -------
    matplotlib.scale.ScaleBase
        A `~matplotlib.scale.ScaleBase` instance.

    See also
    --------
    matplotlib.scale.ScaleBase
    ultraplot.scale.LinearScale
    ultraplot.axes.CartesianAxes.format
    ultraplot.axes.CartesianAxes.dualx
    ultraplot.axes.CartesianAxes.dualy
    """  # noqa: E501
    # NOTE: Why not try to interpret FuncScale arguments, like when lists
    # of numbers are passed to Locator? Because FuncScale *itself* accepts
    # ScaleBase classes as arguments... but constructor functions cannot
    # do anything but return the class instance upon receiving one.
    if np.iterable(scale) and not isinstance(scale, str):
        scale, *args = *scale, *args
    if isinstance(scale, mscale.ScaleBase):
        return copy.copy(scale)
    if not isinstance(scale, str):
        raise ValueError(f"Invalid scale name {scale!r}. Must be string.")
    scale = scale.lower()
    if scale in SCALES_PRESETS:
        if args or kwargs:
            warnings._warn_ultraplot(
                f"Scale {scale!r} is a scale *preset*. Ignoring positional "
                "argument(s): {args} and keyword argument(s): {kwargs}. "
            )
        scale, *args = SCALES_PRESETS[scale]
    if scale in SCALES:
        scale = SCALES[scale]
    else:
        raise ValueError(
            f"Unknown scale or preset {scale!r}. Options are: "
            + ", ".join(map(repr, (*SCALES, *SCALES_PRESETS)))
            + "."
        )
    return scale(*args, **kwargs)


def Proj(
    name,
    backend=None,
    lon0=None,
    lon_0=None,
    lat0=None,
    lat_0=None,
    lonlim=None,
    latlim=None,
    **kwargs,
):
    """
    Return a `cartopy.crs.Projection` or `~mpl_toolkits.basemap.Basemap` instance.

    Parameters
    ----------
    name : str, `cartopy.crs.Projection`, or `~mpl_toolkits.basemap.Basemap`
        The projection name or projection class instance. If the latter, it
        is simply returned. If the former, it must correspond to one of the
        `PROJ <https://proj.org>`__ projection name shorthands, like in
        basemap.

        The following table lists the valid projection name shorthands,
        their full names (with links to the relevant `PROJ documentation
        <https://proj.org/operations/projections>`__),
        and whether they are available in the cartopy and basemap packages.
        (added) indicates a projection class that ultraplot has "added" to
        cartopy using the cartopy API.

        .. _proj_table:

        =============  ===============================================  =========  =======
        Key            Name                                             Cartopy    Basemap
        =============  ===============================================  =========  =======
        ``'aea'``      `Albers Equal Area <aea_>`_                      ✓          ✓
        ``'aeqd'``     `Azimuthal Equidistant <aeqd_>`_                 ✓          ✓
        ``'aitoff'``   `Aitoff <aitoff_>`_                              ✓ (added)  ✗
        ``'cass'``     `Cassini-Soldner <cass_>`_                       ✗          ✓
        ``'cea'``      `Cylindrical Equal Area <cea_>`_                 ✗          ✓
        ``'cyl'``      `Cylindrical Equidistant <eqc_>`_                ✓          ✓
        ``'eck1'``     `Eckert I <eck1_>`_                              ✓          ✗
        ``'eck2'``     `Eckert II <eck2_>`_                             ✓          ✗
        ``'eck3'``     `Eckert III <eck3_>`_                            ✓          ✗
        ``'eck4'``     `Eckert IV <eck4_>`_                             ✓          ✓
        ``'eck5'``     `Eckert V <eck5_>`_                              ✓          ✗
        ``'eck6'``     `Eckert VI <eck6_>`_                             ✓          ✗
        ``'eqdc'``     `Equidistant Conic <eqdc_>`_                     ✓          ✓
        ``'eqc'``      `Cylindrical Equidistant <eqc_>`_                ✓          ✓
        ``'eqearth'``  `Equal Earth <eqearth_>`_                        ✓          ✗
        ``'europp'``   Euro PP (Europe)                                 ✓          ✗
        ``'gall'``     `Gall Stereographic Cylindrical <gall_>`_        ✗          ✓
        ``'geos'``     `Geostationary <geos_>`_                         ✓          ✓
        ``'gnom'``     `Gnomonic <gnom_>`_                              ✓          ✓
        ``'hammer'``   `Hammer <hammer_>`_                              ✓ (added)  ✓
        ``'igh'``      `Interrupted Goode Homolosine <igh_>`_           ✓          ✗
        ``'kav7'``     `Kavrayskiy VII <kav7_>`_                        ✓ (added)  ✓
        ``'laea'``     `Lambert Azimuthal Equal Area <laea_>`_          ✓          ✓
        ``'lcc'``      `Lambert Conformal <lcc_>`_                      ✓          ✓
        ``'lcyl'``     Lambert Cylindrical                              ✓          ✗
        ``'mbtfpq'``   `McBryde-Thomas Flat-Polar Quartic <mbtfpq_>`_   ✗          ✓
        ``'merc'``     `Mercator <merc_>`_                              ✓          ✓
        ``'mill'``     `Miller Cylindrical <mill_>`_                    ✓          ✓
        ``'moll'``     `Mollweide <moll_>`_                             ✓          ✓
        ``'npaeqd'``   North-Polar Azimuthal Equidistant                ✓ (added)  ✓
        ``'npgnom'``   North-Polar Gnomonic                             ✓ (added)  ✗
        ``'nplaea'``   North-Polar Lambert Azimuthal                    ✓ (added)  ✓
        ``'npstere'``  North-Polar Stereographic                        ✓          ✓
        ``'nsper'``    `Near-Sided Perspective <nsper_>`_               ✓          ✓
        ``'osni'``     OSNI (Ireland)                                   ✓          ✗
        ``'osgb'``     OSGB (UK)                                        ✓          ✗
        ``'omerc'``    `Oblique Mercator <omerc_>`_                     ✗          ✓
        ``'ortho'``    `Orthographic <ortho_>`_                         ✓          ✓
        ``'pcarree'``  `Cylindrical Equidistant <eqc_>`_                ✓          ✓
        ``'poly'``     `Polyconic <poly_>`_                             ✗          ✓
        ``'rotpole'``  Rotated Pole                                     ✓          ✓
        ``'sinu'``     `Sinusoidal <sinu_>`_                            ✓          ✓
        ``'spaeqd'``   South-Polar Azimuthal Equidistant                ✓ (added)  ✓
        ``'spgnom'``   South-Polar Gnomonic                             ✓ (added)  ✗
        ``'splaea'``   South-Polar Lambert Azimuthal                    ✓ (added)  ✓
        ``'spstere'``  South-Polar Stereographic                        ✓          ✓
        ``'stere'``    `Stereographic <stere_>`_                        ✓          ✓
        ``'tmerc'``    `Transverse Mercator <tmerc_>`_                  ✓          ✓
        ``'utm'``      `Universal Transverse Mercator <utm_>`_          ✓          ✗
        ``'vandg'``    `van der Grinten <vandg_>`_                      ✗          ✓
        ``'wintri'``   `Winkel tripel <wintri_>`_                       ✓ (added)  ✗
        =============  ===============================================  =========  =======

    backend : {'cartopy', 'basemap'}, default: :rc:`geo.backend`
        Whether to return a cartopy `~cartopy.crs.Projection` instance
        or a basemap `~mpl_toolkits.basemap.Basemap` instance.
    lon0, lat0 : float, optional
        The central projection longitude and latitude. These are translated to
        `central_longitude`, `central_latitude` for cartopy projections.
    lon_0, lat_0 : float, optional
        Aliases for `lon0`, `lat0`.
    lonlim : 2-tuple of float, optional
        The longitude limits. Translated to `min_longitude` and `max_longitude` for
        cartopy projections and `llcrnrlon` and `urcrnrlon` for basemap projections.
    latlim : 2-tuple of float, optional
        The latitude limits. Translated to `min_latitude` and `max_latitude` for
        cartopy projections and `llcrnrlon` and `urcrnrlon` for basemap projections.

    Other parameters
    ----------------
    **kwargs
        Passed to the cartopy `~cartopy.crs.Projection` or
        basemap `~mpl_toolkits.basemap.Basemap` class.

    Returns
    -------
    proj : mpl_toolkits.basemap.Basemap or cartopy.crs.Projection
        A cartopy or basemap projection instance.

    See also
    --------
    mpl_toolkits.basemap.Basemap
    cartopy.crs.Projection
    ultraplot.ui.subplots
    ultraplot.axes.GeoAxes

    References
    ----------
    For more information on map projections, see the
    `wikipedia page <https://en.wikipedia.org/wiki/Map_projection>`__ and the
    `PROJ <https://proj.org>`__ documentation.

    .. _aea: https://proj.org/operations/projections/aea.html
    .. _aeqd: https://proj.org/operations/projections/aeqd.html
    .. _aitoff: https://proj.org/operations/projections/aitoff.html
    .. _cass: https://proj.org/operations/projections/cass.html
    .. _cea: https://proj.org/operations/projections/cea.html
    .. _eqc: https://proj.org/operations/projections/eqc.html
    .. _eck1: https://proj.org/operations/projections/eck1.html
    .. _eck2: https://proj.org/operations/projections/eck2.html
    .. _eck3: https://proj.org/operations/projections/eck3.html
    .. _eck4: https://proj.org/operations/projections/eck4.html
    .. _eck5: https://proj.org/operations/projections/eck5.html
    .. _eck6: https://proj.org/operations/projections/eck6.html
    .. _eqdc: https://proj.org/operations/projections/eqdc.html
    .. _eqc: https://proj.org/operations/projections/eqc.html
    .. _eqearth: https://proj.org/operations/projections/eqearth.html
    .. _gall: https://proj.org/operations/projections/gall.html
    .. _geos: https://proj.org/operations/projections/geos.html
    .. _gnom: https://proj.org/operations/projections/gnom.html
    .. _hammer: https://proj.org/operations/projections/hammer.html
    .. _igh: https://proj.org/operations/projections/igh.html
    .. _kav7: https://proj.org/operations/projections/kav7.html
    .. _laea: https://proj.org/operations/projections/laea.html
    .. _lcc: https://proj.org/operations/projections/lcc.html
    .. _mbtfpq: https://proj.org/operations/projections/mbtfpq.html
    .. _merc: https://proj.org/operations/projections/merc.html
    .. _mill: https://proj.org/operations/projections/mill.html
    .. _moll: https://proj.org/operations/projections/moll.html
    .. _nsper: https://proj.org/operations/projections/nsper.html
    .. _omerc: https://proj.org/operations/projections/omerc.html
    .. _ortho: https://proj.org/operations/projections/ortho.html
    .. _eqc: https://proj.org/operations/projections/eqc.html
    .. _poly: https://proj.org/operations/projections/poly.html
    .. _sinu: https://proj.org/operations/projections/sinu.html
    .. _stere: https://proj.org/operations/projections/stere.html
    .. _tmerc: https://proj.org/operations/projections/tmerc.html
    .. _utm: https://proj.org/operations/projections/utm.html
    .. _vandg: https://proj.org/operations/projections/vandg.html
    .. _wintri: https://proj.org/operations/projections/wintri.html
    """  # noqa: E501
    # Parse input arguments
    # NOTE: Underscores are permitted for consistency with cartopy only here.
    # In format() underscores are not allowed for constistency with reset of API.
    lon0 = _not_none(lon0=lon0, lon_0=lon_0)
    lat0 = _not_none(lat0=lat0, lat_0=lat_0)
    lonlim = _not_none(lonlim, default=(None, None))
    latlim = _not_none(latlim, default=(None, None))
    is_crs = Projection is not object and isinstance(name, Projection)
    is_basemap = Basemap is not object and isinstance(name, Basemap)
    include_axes = kwargs.pop("include_axes", False)  # for error message
    if backend is not None and backend not in ("cartopy", "basemap"):
        raise ValueError(
            f"Invalid backend={backend!r}. Options are 'cartopy' or 'basemap'."
        )
    if not is_crs and not is_basemap:
        backend = _not_none(backend, rc["geo.backend"])
        if not isinstance(name, str):
            raise ValueError(
                f"Unexpected projection {name!r}. Must be PROJ string name, "
                "cartopy.crs.Projection, or mpl_toolkits.basemap.Basemap."
            )
    for key_proj, key_cartopy, value in (
        ("lon_0", "central_longitude", lon0),
        ("lat_0", "central_latitude", lat0),
        ("llcrnrlon", "min_longitude", lonlim[0]),
        ("urcrnrlon", "max_longitude", lonlim[1]),
        ("llcrnrlat", "min_latitude", latlim[0]),
        ("urcrnrlat", "max_latitude", latlim[1]),
    ):
        if value is None:
            continue
        if backend == "basemap" and key_proj == "lon_0" and value > 0:
            value -= 360  # see above comment
        kwargs[key_proj if backend == "basemap" else key_cartopy] = value

    # Projection instances
    if is_crs or is_basemap:
        if backend is not None:
            kwargs["backend"] = backend
        if kwargs:
            warnings._warn_ultraplot(f"Ignoring Proj() keyword arg(s): {kwargs!r}.")
        proj = name
        backend = "cartopy" if is_crs else "basemap"

    # Cartopy name
    # NOTE: Error message matches basemap invalid projection message
    elif backend == "cartopy":
        # Parse keywoard arguments
        import cartopy  # ensure present  # noqa: F401

        for key in ("round", "boundinglat"):
            value = kwargs.pop(key, None)
            if value is not None:
                raise ValueError(
                    "Ignoring Proj() keyword {key}={value!r}. Must be passed "
                    "to GeoAxes.format() when cartopy is the backend."
                )

        # Retrieve projection and initialize with nice error message
        try:
            crs = PROJS[name]
        except KeyError:
            message = f"{name!r} is an unknown cartopy projection class.\n"
            message += "The known cartopy projection classes are:\n"
            message += "\n".join(
                " " + key + " " * (max(map(len, PROJS)) - len(key) + 10) + cls.__name__
                for key, cls in PROJS.items()
            )
            if include_axes:
                from . import axes as paxes  # avoid circular imports

                message = message.replace("class.", "class or axes subclass.")
                message += "\nThe known axes subclasses are:\n" + paxes._cls_table
            raise ValueError(message) from None
        if name == "geos":  # fix common mistake
            kwargs.pop("central_latitude", None)
        proj = crs(**kwargs)

    # Basemap name
    # NOTE: Known issue that basemap sometimes produces backwards maps:
    # https://stackoverflow.com/q/56299971/4970632
    # NOTE: We set rsphere to fix non-conda installed basemap issue:
    # https://github.com/matplotlib/basemap/issues/361
    # NOTE: Adjust lon_0 to fix issues with Robinson (and related?) projections
    # https://stackoverflow.com/questions/56299971/ (also triggers 'no room for axes')
    # NOTE: Unlike cartopy, basemap resolution is configured
    # on initialization and controls *all* features.
    else:
        # Parse input arguments
        from mpl_toolkits import basemap  # ensure present  # noqa: F401

        if name in ("eqc", "pcarree"):
            name = "cyl"  # PROJ package aliases
        defaults = {"fix_aspect": True, **PROJ_DEFAULTS.get(name, {})}
        if name[:2] in ("np", "sp"):
            defaults["round"] = rc["geo.round"]
        if name == "geos":
            defaults["rsphere"] = (6378137.00, 6356752.3142)
        for key, value in defaults.items():
            if kwargs.get(key, None) is None:  # allow e.g. boundinglat=None
                kwargs[key] = value

        reso = _not_none(
            reso=kwargs.pop("reso", None),
            resolution=kwargs.pop("resolution", None),
            default=rc["reso"],
        )
        if reso in RESOS_BASEMAP:
            reso = RESOS_BASEMAP[reso]
        else:
            raise ValueError(
                f"Invalid resolution {reso!r}. Options are: "
                + ", ".join(map(repr, RESOS_BASEMAP))
                + "."
            )
        kwargs.update({"resolution": reso, "projection": name})
        try:
            proj = Basemap(**kwargs)  # will raise helpful warning
        except ValueError as err:
            message = str(err)
            message = message.strip()
            message = message.replace("projection", "basemap projection")
            message = message.replace("supported", "known")
            if include_axes:
                from . import axes as paxes  # avoid circular imports

                message = message.replace("projection.", "projection or axes subclass.")
                message += "\nThe known axes subclasses are:\n" + paxes._cls_table
            raise ValueError(message) from None

    proj._proj_backend = backend
    return proj


# Deprecated
Colors = warnings._rename_objs("0.8.0", Colors=get_colors)
