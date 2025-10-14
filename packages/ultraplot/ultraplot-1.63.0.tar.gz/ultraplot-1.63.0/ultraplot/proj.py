#!/usr/bin/env python3
"""
Additional cartopy projection classes.
"""
import warnings

from .internals import ic  # noqa: F401
from .internals import docstring

try:
    from cartopy.crs import (  # stereo projections needed in geo.py
        AzimuthalEquidistant,
        Gnomonic,
        LambertAzimuthalEqualArea,
        NorthPolarStereo,
        SouthPolarStereo,
        _WarpedRectangularProjection,
    )
except ModuleNotFoundError:
    AzimuthalEquidistant = Gnomonic = LambertAzimuthalEqualArea = object
    _WarpedRectangularProjection = NorthPolarStereo = SouthPolarStereo = object

__all__ = [
    "Aitoff",
    "Hammer",
    "KavrayskiyVII",
    "WinkelTripel",
    "NorthPolarAzimuthalEquidistant",
    "SouthPolarAzimuthalEquidistant",
    "NorthPolarGnomonic",
    "SouthPolarGnomonic",
    "NorthPolarLambertAzimuthalEqualArea",
    "SouthPolarLambertAzimuthalEqualArea",
]


_reso_docstring = """
The projection resolution.
"""
_init_docstring = """
Parameters
----------
central_longitude : float, default: 0
    The central meridian longitude in degrees.
false_easting: float, default: 0
    X offset from planar origin in metres.
false_northing: float, default: 0
    Y offset from planar origin in metres.
globe : `~cartopy.crs.Globe`, optional
    If omitted, a default globe is created.
"""
docstring._snippet_manager["proj.reso"] = _reso_docstring
docstring._snippet_manager["proj.init"] = _init_docstring


class Aitoff(_WarpedRectangularProjection):
    """
    The `Aitoff <https://en.wikipedia.org/wiki/Aitoff_projection>`__ projection.
    """

    #: Registered projection name.
    name = "aitoff"

    @docstring._snippet_manager
    def __init__(
        self, central_longitude=0, globe=None, false_easting=None, false_northing=None
    ):
        """
        %(proj.init)s
        """
        from cartopy.crs import WGS84_SEMIMAJOR_AXIS, Globe

        if globe is None:
            globe = Globe(semimajor_axis=WGS84_SEMIMAJOR_AXIS, ellipse=None)

        a = globe.semimajor_axis or WGS84_SEMIMAJOR_AXIS
        b = globe.semiminor_axis or a
        if b != a or globe.ellipse is not None:
            warnings.warn(
                f"The {self.name!r} projection does not handle elliptical globes."
            )

        proj4_params = {"proj": "aitoff", "lon_0": central_longitude}
        super().__init__(
            proj4_params,
            central_longitude,
            false_easting=false_easting,
            false_northing=false_northing,
            globe=globe,
        )

    @docstring._snippet_manager
    @property
    def threshold(self):  # how finely to interpolate line data, etc.
        """
        %(proj.reso)s
        """
        return 1e5


class Hammer(_WarpedRectangularProjection):
    """
    The `Hammer <https://en.wikipedia.org/wiki/Hammer_projection>`__ projection.
    """

    #: Registered projection name.
    name = "hammer"

    @docstring._snippet_manager
    def __init__(
        self, central_longitude=0, globe=None, false_easting=None, false_northing=None
    ):
        """
        %(proj.init)s
        """
        from cartopy.crs import WGS84_SEMIMAJOR_AXIS, Globe

        if globe is None:
            globe = Globe(semimajor_axis=WGS84_SEMIMAJOR_AXIS, ellipse=None)

        a = globe.semimajor_axis or WGS84_SEMIMAJOR_AXIS
        b = globe.semiminor_axis or a
        if b != a or globe.ellipse is not None:
            warnings.warn(
                f"The {self.name!r} projection does not handle elliptical globes."
            )

        proj4_params = {"proj": "hammer", "lon_0": central_longitude}
        super().__init__(
            proj4_params,
            central_longitude,
            false_easting=false_easting,
            false_northing=false_northing,
            globe=globe,
        )

    @docstring._snippet_manager
    @property
    def threshold(self):  # how finely to interpolate line data, etc.
        """
        %(proj.reso)s
        """
        return 1e5


class KavrayskiyVII(_WarpedRectangularProjection):
    """
    The `Kavrayskiy VII \
<https://en.wikipedia.org/wiki/Kavrayskiy_VII_projection>`__ projection.
    """

    #: Registered projection name.
    name = "kavrayskiyVII"

    @docstring._snippet_manager
    def __init__(
        self, central_longitude=0, globe=None, false_easting=None, false_northing=None
    ):
        """
        %(proj.init)s
        """
        from cartopy.crs import WGS84_SEMIMAJOR_AXIS, Globe

        if globe is None:
            globe = Globe(semimajor_axis=WGS84_SEMIMAJOR_AXIS, ellipse=None)

        a = globe.semimajor_axis or WGS84_SEMIMAJOR_AXIS
        b = globe.semiminor_axis or a
        if b != a or globe.ellipse is not None:
            warnings.warn(
                f"The {self.name!r} projection does not handle elliptical globes."
            )

        proj4_params = {"proj": "kav7", "lon_0": central_longitude}
        super().__init__(
            proj4_params,
            central_longitude,
            false_easting=false_easting,
            false_northing=false_northing,
            globe=globe,
        )

    @docstring._snippet_manager
    @property
    def threshold(self):
        """
        %(proj.reso)s
        """
        return 1e5


class WinkelTripel(_WarpedRectangularProjection):
    """
    The `Winkel tripel (Winkel III) \
<https://en.wikipedia.org/wiki/Winkel_tripel_projection>`__ projection.
    """

    #: Registered projection name.
    name = "winkeltripel"

    @docstring._snippet_manager
    def __init__(
        self, central_longitude=0, globe=None, false_easting=None, false_northing=None
    ):
        """
        %(proj.init)s
        """
        from cartopy.crs import WGS84_SEMIMAJOR_AXIS, Globe

        if globe is None:
            globe = Globe(semimajor_axis=WGS84_SEMIMAJOR_AXIS, ellipse=None)

        a = globe.semimajor_axis or WGS84_SEMIMAJOR_AXIS
        b = globe.semiminor_axis or a
        if b != a or globe.ellipse is not None:
            warnings.warn(
                f"The {self.name!r} projection does not handle " "elliptical globes."
            )

        proj4_params = {"proj": "wintri", "lon_0": central_longitude}
        super().__init__(
            proj4_params,
            central_longitude,
            false_easting=false_easting,
            false_northing=false_northing,
            globe=globe,
        )

    @docstring._snippet_manager
    @property
    def threshold(self):
        """
        %(proj.reso)s
        """
        return 1e5


class NorthPolarAzimuthalEquidistant(AzimuthalEquidistant):
    """
    Analogous to `~cartopy.crs.NorthPolarStereo`.
    """

    @docstring._snippet_manager
    def __init__(self, central_longitude=0.0, globe=None):
        """
        %(proj.init)s
        """
        super().__init__(
            central_latitude=90, central_longitude=central_longitude, globe=globe
        )


class SouthPolarAzimuthalEquidistant(AzimuthalEquidistant):
    """
    Analogous to `~cartopy.crs.SouthPolarStereo`.
    """

    @docstring._snippet_manager
    def __init__(self, central_longitude=0.0, globe=None):
        """
        %(proj.init)s
        """
        super().__init__(
            central_latitude=-90, central_longitude=central_longitude, globe=globe
        )


class NorthPolarLambertAzimuthalEqualArea(LambertAzimuthalEqualArea):
    """
    Analogous to `~cartopy.crs.NorthPolarStereo`.
    """

    @docstring._snippet_manager
    def __init__(self, central_longitude=0.0, globe=None):
        """
        %(proj.init)s
        """
        super().__init__(
            central_latitude=90, central_longitude=central_longitude, globe=globe
        )


class SouthPolarLambertAzimuthalEqualArea(LambertAzimuthalEqualArea):
    """
    Analogous to `~cartopy.crs.SouthPolarStereo`.
    """

    @docstring._snippet_manager
    def __init__(self, central_longitude=0.0, globe=None):
        """
        %(proj.init)s
        """
        super().__init__(
            central_latitude=-90, central_longitude=central_longitude, globe=globe
        )


class NorthPolarGnomonic(Gnomonic):
    """
    Analogous to `~cartopy.crs.NorthPolarStereo`.
    """

    @docstring._snippet_manager
    def __init__(self, central_longitude=0.0, globe=None):
        """
        %(proj.init)s
        """
        super().__init__(
            central_latitude=90, central_longitude=central_longitude, globe=globe
        )


class SouthPolarGnomonic(Gnomonic):
    """
    Analogous to `~cartopy.crs.SouthPolarStereo`.
    """

    @docstring._snippet_manager
    def __init__(self, central_longitude=0.0, globe=None):
        """
        %(proj.init)s
        """
        super().__init__(
            central_latitude=-90, central_longitude=central_longitude, globe=globe
        )
