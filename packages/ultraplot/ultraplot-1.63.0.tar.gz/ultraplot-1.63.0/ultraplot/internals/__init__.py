#!/usr/bin/env python3
"""
Internal utilities.
"""
# Import statements
import inspect
from numbers import Integral, Real

import numpy as np
from matplotlib import rcParams as rc_matplotlib

try:  # print debugging (used with internal modules)
    from icecream import ic
except ImportError:  # graceful fallback if IceCream isn't installed
    ic = lambda *args: print(*args)  # noqa: E731

from . import warnings as warns


def _not_none(*args, default=None, **kwargs):
    """
    Return the first non-``None`` value. This is used with keyword arg aliases and
    for setting default values. Use `kwargs` to issue warnings when multiple passed.
    """
    first = default
    if args and kwargs:
        raise ValueError("_not_none can only be used with args or kwargs.")
    elif args:
        for arg in args:
            if arg is not None:
                first = arg
                break
    elif kwargs:
        for name, arg in list(kwargs.items()):
            if arg is not None:
                first = arg
                break
        kwargs = {name: arg for name, arg in kwargs.items() if arg is not None}
        if len(kwargs) > 1:
            warnings._warn_ultraplot(
                f"Got conflicting or duplicate keyword arguments: {kwargs}. "
                "Using the first keyword argument."
            )
    return first


# Internal import statements
# WARNING: Must come after _not_none because this is leveraged inside other funcs
from . import (  # noqa: F401
    benchmarks,
    context,
    docstring,
    fonts,
    guides,
    inputs,
    labels,
    rcsetup,
    versions,
    warnings,
)
from .versions import _version_mpl, _version_cartopy  # noqa: F401
from .warnings import UltraPlotWarning  # noqa: F401


# Style aliases. We use this rather than matplotlib's normalize_kwargs and _alias_maps.
# NOTE: We add aliases 'edgewidth' and 'fillcolor' for patch edges and faces
# NOTE: Alias cannot appear as key or else _translate_kwargs will overwrite with None!
_alias_maps = {
    "rgba": {
        "red": ("r",),
        "green": ("g",),
        "blue": ("b",),
        "alpha": ("a",),
    },
    "hsla": {
        "hue": ("h",),
        "saturation": ("s", "c", "chroma"),
        "luminance": ("l",),
        "alpha": ("a",),
    },
    "patch": {
        "alpha": (
            "a",
            "alphas",
            "fa",
            "facealpha",
            "facealphas",
            "fillalpha",
            "fillalphas",
        ),  # noqa: E501
        "color": ("c", "colors"),
        "edgecolor": ("ec", "edgecolors"),
        "facecolor": ("fc", "facecolors", "fillcolor", "fillcolors"),
        "hatch": ("h", "hatching"),
        "linestyle": ("ls", "linestyles"),
        "linewidth": ("lw", "linewidths", "ew", "edgewidth", "edgewidths"),
        "zorder": ("z", "zorders"),
    },
    "line": {  # copied from lines.py but expanded to include plurals
        "alpha": ("a", "alphas"),
        "color": ("c", "colors"),
        "dashes": ("d", "dash"),
        "drawstyle": ("ds", "drawstyles"),
        "fillstyle": ("fs", "fillstyles", "mfs", "markerfillstyle", "markerfillstyles"),
        "linestyle": ("ls", "linestyles"),
        "linewidth": ("lw", "linewidths"),
        "marker": ("m", "markers"),
        "markersize": ("s", "ms", "markersizes"),  # WARNING: no 'sizes' here for barb
        "markeredgewidth": ("ew", "edgewidth", "edgewidths", "mew", "markeredgewidths"),
        "markeredgecolor": ("ec", "edgecolor", "edgecolors", "mec", "markeredgecolors"),
        "markerfacecolor": (
            "fc",
            "facecolor",
            "facecolors",
            "fillcolor",
            "fillcolors",
            "mc",
            "markercolor",
            "markercolors",
            "mfc",
            "markerfacecolors",
        ),
        "zorder": ("z", "zorders"),
    },
    "collection": {  # WARNING: face color ignored for line collections
        "alpha": ("a", "alphas"),  # WARNING: collections and contours use singular!
        "colors": ("c", "color"),
        "edgecolors": ("ec", "edgecolor", "mec", "markeredgecolor", "markeredgecolors"),
        "facecolors": (
            "fc",
            "facecolor",
            "fillcolor",
            "fillcolors",
            "mc",
            "markercolor",
            "markercolors",
            "mfc",
            "markerfacecolor",
            "markerfacecolors",  # noqa: E501
        ),
        "linestyles": ("ls", "linestyle"),
        "linewidths": (
            "lw",
            "linewidth",
            "ew",
            "edgewidth",
            "edgewidths",
            "mew",
            "markeredgewidth",
            "markeredgewidths",
        ),  # noqa: E501
        "marker": ("m", "markers"),
        "sizes": ("s", "ms", "markersize", "markersizes"),
        "zorder": ("z", "zorders"),
    },
    "text": {
        "color": ("c", "fontcolor"),  # NOTE: see text.py source code
        "fontfamily": ("family", "name", "fontname"),
        "fontsize": ("size",),
        "fontstretch": ("stretch",),
        "fontstyle": ("style",),
        "fontvariant": ("variant",),
        "fontweight": ("weight",),
        "fontproperties": ("fp", "font", "font_properties"),
        "zorder": ("z", "zorders"),
    },
}


# Unit docstrings
# NOTE: Try to fit this into a single line. Cannot break up with newline as that will
# mess up docstring indentation since this is placed in indented param lines.
_units_docstring = "If float, units are {units}. If string, interpreted by `~ultraplot.utils.units`."  # noqa: E501
docstring._snippet_manager["units.pt"] = _units_docstring.format(units="points")
docstring._snippet_manager["units.in"] = _units_docstring.format(units="inches")
docstring._snippet_manager["units.em"] = _units_docstring.format(units="em-widths")


# Style docstrings
# NOTE: These are needed in a few different places
_line_docstring = """
lw, linewidth, linewidths : unit-spec, default: :rc:`lines.linewidth`
    The width of the line(s).
    %(units.pt)s
ls, linestyle, linestyles : str, default: :rc:`lines.linestyle`
    The style of the line(s).
c, color, colors : color-spec, optional
    The color of the line(s). The property `cycle` is used by default.
a, alpha, alphas : float, optional
    The opacity of the line(s). Inferred from `color` by default.
"""
_patch_docstring = """
lw, linewidth, linewidths : unit-spec, default: :rc:`patch.linewidth`
    The edge width of the patch(es).
    %(units.pt)s
ls, linestyle, linestyles : str, default: '-'
    The edge style of the patch(es).
ec, edgecolor, edgecolors : color-spec, default: '{edgecolor}'
    The edge color of the patch(es).
fc, facecolor, facecolors, fillcolor, fillcolors : color-spec, optional
    The face color of the patch(es). The property `cycle` is used by default.
a, alpha, alphas : float, optional
    The opacity of the patch(es). Inferred from `facecolor` and `edgecolor` by default.
"""
_pcolor_collection_docstring = """
lw, linewidth, linewidths : unit-spec, default: 0.3
    The width of lines between grid boxes.
    %(units.pt)s
ls, linestyle, linestyles : str, default: '-'
    The style of lines between grid boxes.
ec, edgecolor, edgecolors : color-spec, default: 'k'
    The color of lines between grid boxes.
a, alpha, alphas : float, optional
    The opacity of the grid boxes. Inferred from `cmap` by default.
"""
_contour_collection_docstring = """
lw, linewidth, linewidths : unit-spec, default: 0.3 or :rc:`lines.linewidth`
    The width of the line contours. Default is ``0.3`` when adding to filled contours
    or :rc:`lines.linewidth` otherwise. %(units.pt)s
ls, linestyle, linestyles : str, default: '-' or :rc:`contour.negative_linestyle`
    The style of the line contours. Default is ``'-'`` for positive contours and
    :rcraw:`contour.negative_linestyle` for negative contours.
ec, edgecolor, edgecolors : color-spec, default: 'k' or inferred
    The color of the line contours. Default is ``'k'`` when adding to filled contours
    or inferred from `color` or `cmap` otherwise.
a, alpha, alpha : float, optional
    The opacity of the contours. Inferred from `edgecolor` by default.
"""
_text_docstring = """
name, fontname, family, fontfamily : str, optional
    The font typeface name (e.g., ``'Fira Math'``) or font family name (e.g.,
    ``'serif'``). Matplotlib falls back to the system default if not found.
size, fontsize : unit-spec or str, optional
    The font size. %(units.pt)s
    This can also be a string indicating some scaling relative to
    :rcraw:`font.size`. The sizes and scalings are shown below. The
    scalings ``'med'``, ``'med-small'``, and ``'med-large'`` are
    added by ultraplot while the rest are native matplotlib sizes.

    .. _font_table:

    ==========================  =====
    Size                        Scale
    ==========================  =====
    ``'xx-small'``              0.579
    ``'x-small'``               0.694
    ``'small'``, ``'smaller'``  0.833
    ``'med-small'``             0.9
    ``'med'``, ``'medium'``     1.0
    ``'med-large'``             1.1
    ``'large'``, ``'larger'``   1.2
    ``'x-large'``               1.440
    ``'xx-large'``              1.728
    ``'larger'``                1.2
    ==========================  =====

"""
docstring._snippet_manager["artist.line"] = _line_docstring
docstring._snippet_manager["artist.text"] = _text_docstring
docstring._snippet_manager["artist.patch"] = _patch_docstring.format(edgecolor="none")
docstring._snippet_manager["artist.patch_black"] = _patch_docstring.format(
    edgecolor="black"
)  # noqa: E501
docstring._snippet_manager["artist.collection_pcolor"] = _pcolor_collection_docstring
docstring._snippet_manager["artist.collection_contour"] = _contour_collection_docstring


def _get_aliases(category, *keys):
    """
    Get all available aliases.
    """
    aliases = []
    for key in keys:
        aliases.append(key)
        aliases.extend(_alias_maps[category][key])
    return tuple(aliases)


def _kwargs_to_args(options, *args, allow_extra=False, **kwargs):
    """
    Translate keyword arguments to positional arguments. Permit omitted
    arguments so that plotting functions can infer values.
    """
    nargs, nopts = len(args), len(options)
    if nargs > nopts and not allow_extra:
        raise ValueError(f"Expected up to {nopts} positional arguments. Got {nargs}.")
    args = list(args)  # WARNING: Axes.text() expects return type of list
    args.extend(None for _ in range(nopts - nargs))  # fill missing args
    for idx, keys in enumerate(options):
        if isinstance(keys, str):
            keys = (keys,)
        opts = {}
        if args[idx] is not None:  # positional args have first priority
            opts[keys[0] + "_positional"] = args[idx]
        for key in keys:  # keyword args
            opts[key] = kwargs.pop(key, None)
        args[idx] = _not_none(**opts)  # may reassign None
    return args, kwargs


def _pop_kwargs(kwargs, *keys, **aliases):
    """
    Pop the input properties and return them in a new dictionary.
    """
    output = {}
    aliases.update({key: () for key in keys})
    for key, aliases in aliases.items():
        aliases = (aliases,) if isinstance(aliases, str) else aliases
        opts = {key: kwargs.pop(key, None) for key in (key, *aliases)}
        value = _not_none(**opts)
        if value is not None:
            output[key] = value
    return output


def _pop_params(kwargs, *funcs, ignore_internal=False):
    """
    Pop parameters of the input functions or methods.
    """
    internal_params = {
        "default_cmap",
        "default_discrete",
        "inbounds",
        "plot_contours",
        "plot_lines",
        "skip_autolev",
        "to_centers",
    }
    output = {}
    for func in funcs:
        if isinstance(func, inspect.Signature):
            sig = func
        elif callable(func):
            sig = inspect.signature(func)
        elif func is None:
            continue
        else:
            raise RuntimeError(f"Internal error. Invalid function {func!r}.")
        for key in sig.parameters:
            value = kwargs.pop(key, None)
            if ignore_internal and key in internal_params:
                continue
            if value is not None:
                output[key] = value
    return output


def _pop_props(input, *categories, prefix=None, ignore=None, skip=None):
    """
    Pop the registered properties and return them in a new dictionary.
    """
    output = {}
    skip = skip or ()
    ignore = ignore or ()
    if isinstance(skip, str):  # e.g. 'sizes' for barbs() input
        skip = (skip,)
    if isinstance(ignore, str):  # e.g. 'marker' to ignore marker properties
        ignore = (ignore,)
    prefix = prefix or ""  # e.g. 'box' for boxlw, boxlinewidth, etc.
    for category in categories:
        for key, aliases in _alias_maps[category].items():
            if isinstance(aliases, str):
                aliases = (aliases,)
            opts = {
                prefix + alias: input.pop(prefix + alias, None)
                for alias in (key, *aliases)
                if alias not in skip
            }
            prop = _not_none(**opts)
            if prop is None:
                continue
            if any(string in key for string in ignore):
                warnings._warn_ultraplot(f"Ignoring property {key}={prop!r}.")
                continue
            if isinstance(prop, str):  # ad-hoc unit conversion
                if key in ("fontsize",):
                    from ..utils import _fontsize_to_pt

                    prop = _fontsize_to_pt(prop)
                if key in ("linewidth", "linewidths", "markersize"):
                    from ..utils import units

                    prop = units(prop, "pt")
            output[key] = prop
    return output


def _pop_rc(src, *, ignore_conflicts=True):
    """
    Pop the rc setting names and mode for a `~Configurator.context` block.
    """
    # NOTE: Must ignore deprected or conflicting rc params
    # NOTE: rc_mode == 2 applies only the updated params. A power user
    # could use ax.format(rc_mode=0) to re-apply all the current settings
    conflict_params = (
        "alpha",
        "color",
        "facecolor",
        "edgecolor",
        "linewidth",
        "basemap",
        "backend",
        "share",
        "span",
        "tight",
        "span",
    )
    kw = src.pop("rc_kw", None) or {}
    if "mode" in src:
        src["rc_mode"] = src.pop("mode")
        warnings._warn_ultraplot(
            "Keyword 'mode' was deprecated in v0.6. Please use 'rc_mode' instead."
        )
    mode = src.pop("rc_mode", None)
    mode = _not_none(mode, 2)  # only apply updated params by default
    for key, value in tuple(src.items()):
        name = rcsetup._rc_nodots.get(key, None)
        if ignore_conflicts and name in conflict_params:
            name = None  # former renamed settings
        if name is not None:
            kw[name] = src.pop(key)
    return kw, mode


def _translate_loc(loc, mode, *, default=None, **kwargs):
    """
    Translate the location string `loc` into a standardized form. The `mode`
    must be a string for which there is a :rcraw:`mode.loc` setting. Additional
    options can be added with keyword arguments.
    """
    # Create specific options dictionary
    # NOTE: This is not inside validators.py because it is also used to
    # validate various user-input locations.
    if mode == "align":
        loc_dict = rcsetup.ALIGN_LOCS
    elif mode == "panel":
        loc_dict = rcsetup.PANEL_LOCS
    elif mode == "legend":
        loc_dict = rcsetup.LEGEND_LOCS
    elif mode == "colorbar":
        loc_dict = rcsetup.COLORBAR_LOCS
    elif mode == "text":
        loc_dict = rcsetup.TEXT_LOCS
    else:
        raise ValueError(f"Invalid mode {mode!r}.")
    loc_dict = loc_dict.copy()
    loc_dict.update(kwargs)

    # Translate location
    if loc in (None, True):
        loc = default
    elif isinstance(loc, (str, Integral)):
        try:
            loc = loc_dict[loc]
        except KeyError:
            raise KeyError(
                f"Invalid {mode} location {loc!r}. Options are: "
                + ", ".join(map(repr, loc_dict))
                + "."
            )
    elif (
        mode == "legend"
        and np.iterable(loc)
        and len(loc) == 2
        and all(isinstance(l, Real) for l in loc)
    ):
        loc = tuple(loc)
    else:
        raise KeyError(f"Invalid {mode} location {loc!r}.")

    # Kludge / white lie
    # TODO: Implement 'best' colorbar location
    if mode == "colorbar" and loc == "best":
        loc = "lower right"

    return loc


def _translate_grid(b, key):
    """
    Translate an instruction to turn either major or minor gridlines on or off into a
    boolean and string applied to :rcraw:`axes.grid` and :rcraw:`axes.grid.which`.
    """
    ob = rc_matplotlib["axes.grid"]
    owhich = rc_matplotlib["axes.grid.which"]

    # Instruction is to turn off gridlines
    if not b:
        # Gridlines are already off, or they are on for the particular
        # ones that we want to turn off. Instruct to turn both off.
        if (
            not ob
            or key == "grid"
            and owhich == "major"
            or key == "gridminor"
            and owhich == "minor"
        ):
            which = "both"  # disable both sides
        # Gridlines are currently on for major and minor ticks, so we
        # instruct to turn on gridlines for the one we *don't* want off
        elif owhich == "both":  # and ob is True, as already tested
            # if gridminor=False, enable major, and vice versa
            b = True
            which = "major" if key == "gridminor" else "minor"
        # Gridlines are on for the ones that we *didn't* instruct to
        # turn off, and off for the ones we do want to turn off. This
        # just re-asserts the ones that are already on.
        else:
            b = True
            which = owhich

    # Instruction is to turn on gridlines
    else:
        # Gridlines are already both on, or they are off only for the
        # ones that we want to turn on. Turn on gridlines for both.
        if (
            owhich == "both"
            or key == "grid"
            and owhich == "minor"
            or key == "gridminor"
            and owhich == "major"
        ):
            which = "both"
        # Gridlines are off for both, or off for the ones that we
        # don't want to turn on. We can just turn on these ones.
        else:
            which = owhich

    return b, which
