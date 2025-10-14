import ultraplot as uplt, numpy as np, warnings
import pytest
from unittest import mock


@pytest.mark.mpl_image_compare
def test_geographic_single_projection():
    fig = uplt.figure(refwidth=3)
    axs = fig.subplots(nrows=2, proj="robin", proj_kw={"lon_0": 180})
    axs.format(
        suptitle="Figure with single projection",
        land=True,
        latlines=30,
        lonlines=60,
    )
    return fig


@pytest.mark.mpl_image_compare
def test_geographic_multiple_projections():
    fig = uplt.figure(share=0)
    # Add projections
    gs = uplt.GridSpec(ncols=2, nrows=3, hratios=(1, 1, 1.4))
    for i, proj in enumerate(("cyl", "hammer", "npstere")):
        ax1 = fig.subplot(gs[i, 0], proj=proj, basemap=True)  # basemap
        ax2 = fig.subplot(gs[i, 1], proj=proj)  # cartopy

    # Format projections
    fig.format(
        land=True,
        suptitle="Figure with several projections",
        toplabels=("Basemap projections", "Cartopy projections"),
        toplabelweight="normal",
        latlines=30,
        lonlines=60,
        lonlabels="b",
        latlabels="r",  # or lonlabels=True, labels=True, etc.
    )
    fig.subplotgrid[-2:].format(
        latlines=20,
        lonlines=30,
        labels=True,
    )  # dense gridlines for polar plots
    uplt.rc.reset()
    return fig


@pytest.mark.mpl_image_compare
def test_drawing_in_projection_without_globe(rng):
    # Fake data with unusual longitude seam location and without coverage over poles
    offset = -40
    lon = uplt.arange(offset, 360 + offset - 1, 60)
    lat = uplt.arange(-60, 60 + 1, 30)
    data = rng.random((len(lat), len(lon)))

    globe = False
    string = "with" if globe else "without"
    gs = uplt.GridSpec(nrows=2, ncols=2)
    fig = uplt.figure(refwidth=2.5)
    for i, ss in enumerate(gs):
        ax = fig.subplot(ss, proj="kav7", basemap=(i % 2))
        cmap = ("sunset", "sunrise")[i % 2]
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
    return fig


@pytest.mark.mpl_image_compare
def test_drawing_in_projection_with_globe(rng):
    # Fake data with unusual longitude seam location and without coverage over poles
    offset = -40
    lon = uplt.arange(offset, 360 + offset - 1, 60)
    lat = uplt.arange(-60, 60 + 1, 30)
    data = rng.random((len(lat), len(lon)))

    globe = True
    string = "with" if globe else "without"
    gs = uplt.GridSpec(nrows=2, ncols=2)
    fig = uplt.figure(refwidth=2.5)
    for i, ss in enumerate(gs):
        ax = fig.subplot(ss, proj="kav7", basemap=(i % 2))
        cmap = ("sunset", "sunrise")[i % 2]
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
    return fig


@pytest.mark.mpl_image_compare
def test_geoticks():

    lonlim = (-140, 60)
    latlim = (-10, 50)
    basemap_projection = uplt.Proj(
        "cyl",
        lonlim=lonlim,
        latlim=latlim,
        backend="basemap",
    )
    fig, ax = uplt.subplots(
        ncols=3,
        proj=(
            "cyl",  # cartopy
            "cyl",  # cartopy
            basemap_projection,  # basemap
        ),
        share=0,
    )
    settings = dict(land=True, labels=True, lonlines=20, latlines=20)
    # Shows sensible "default"; uses cartopy backend to show the grid lines with ticks
    ax[0].format(
        lonlim=lonlim,
        latlim=latlim,
        **settings,
    )

    # Add lateral ticks only
    ax[1].format(
        latticklen=True,
        gridminor=True,
        lonlim=lonlim,
        latlim=latlim,
        **settings,
    )

    ax[2].format(
        latticklen=5.0,
        lonticklen=2.0,
        grid=False,
        gridminor=False,
        **settings,
    )
    return fig


def test_geoticks_input_handling(recwarn):
    fig, ax = uplt.subplots(proj="aeqd")
    # Should warn that about non-rectilinear projection.
    with pytest.warns(uplt.warnings.UltraPlotWarning):
        ax.format(lonticklen=True)
    # When set to None the latticks are not added.
    # No warnings should be raised.
    ax.format(lonticklen=None)
    assert len(recwarn) == 0
    # Can parse a string
    ax.format(lonticklen="1em")


@pytest.mark.parametrize(
    ("layout", "lonlabels", "latlabels"),
    [
        ([1, 2], "tb", "lr"),
        ([1, 2], "r", "t"),
        ([[1, 2, 3], [4, 5, 3]], "t", "lr"),
    ],
)
@pytest.mark.mpl_image_compare
def test_geoticks_shared(layout, lonlabels, latlabels):
    fig, ax = uplt.subplots(layout, proj="cyl", share="all")
    ax.format(
        latlim=(0, 10),  # smaller rangers are quicker
        lonlim=(0, 10),
        lonlines=10,
        latlines=10,
        land=True,  # enable land
        labels=True,  # enable tick labels
        latticklen=True,  # show ticks
        lonticklen=True,  # show ticks
        grid=True,
        gridminor=False,
        lonlabels=lonlabels,
        latlabels=latlabels,
    )
    return fig


def test_geoticks_shared_non_rectilinear():
    with pytest.warns(uplt.warnings.UltraPlotWarning):
        fig, ax = uplt.subplots(ncols=2, proj="aeqd", share="all")
        ax.format(
            land=True,
            labels=True,
            lonlabels="all",
            latlabels="all",
        )
        fig.canvas.draw()  # draw is necessary to invoke the warning
    uplt.close(fig)


def test_lon0_shifts():
    """
    Check if a shift with lon0 actually shifts the
    view port labels and ticks
    """
    # Note for small enough shifts, e.g. +- 10 we are
    # still showing zero due to the formatting logic
    fig, ax = uplt.subplots(proj="cyl", proj_kw=dict(lon_0=90))
    ax.format(land=True, labels=True)
    locator = ax[0]._lonaxis.get_major_locator()
    formatter = ax[0]._lonaxis.get_major_formatter()
    locs = locator()
    formatted_ticks = np.array([formatter(x) for x in locs])
    for loc, format in zip(locs, formatted_ticks):
        # Get normalized coordinates
        loc = (loc + 180) % 360 - 180
        # Check if the labels are matching the location
        # abs is taken due to north-west
        str_loc = str(abs(int(loc)))
        n = len(str_loc)
        assert str_loc == format[:n], f"Epxected: {str_loc}, got: {format[:n]}"
    assert locs[0] != 0  # we should not be a 0 anymore
    uplt.close(fig)


@pytest.mark.parametrize(
    "layout, expectations",
    [
        (
            # layout 1: 3x3 grid with unique IDs
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9],
            ],
            # expectations: per element ID (1-9), four booleans: [top, right, bottom, left]
            [
                [True, False, False, True],  # 1
                [True, False, False, False],  # 2
                [True, False, True, False],  # 3
                [False, False, False, True],  # 4
                [False, False, False, False],  # 5
                [False, False, True, False],  # 6
                [False, True, False, True],  # 7
                [False, True, False, False],  # 8
                [False, True, True, False],  # 9
            ],
        ),
        (
            # layout 2: shared IDs (merged subplots?)
            [
                [1, 2, 0],
                [1, 2, 5],
                [3, 4, 5],
                [3, 4, 0],
            ],
            # expectations for IDs 1–5: [top, right, bottom, left]
            [
                [True, False, False, True],  # 1
                [True, False, True, False],  # 2
                [False, True, False, True],  # 3
                [False, True, True, False],  # 4
                [True, True, True, True],  # 5
            ],
        ),
    ],
)
def test_sharing_cartopy(layout, expectations):
    def are_labels_on(ax, which=["top", "bottom", "right", "left"]) -> tuple[bool]:
        gl = ax.gridlines_major

        on = [False, False, False, False]
        for idx, labeler in enumerate(which):
            if getattr(gl, f"{labeler}_labels"):
                on[idx] = True
        return on

    settings = dict(land=True, ocean=True, labels="both")
    fig, ax = uplt.subplots(layout, share="all", proj="cyl")
    ax.format(**settings)
    for axi in ax:
        state = are_labels_on(axi)
        expectation = expectations[axi.number - 1]
        for i, j in zip(state, expectation):
            assert i == j
    uplt.close(fig)


def test_toggle_gridliner_labels():
    """
    Test whether we can toggle the labels on or off
    """
    # Cartopy backend
    fig, ax = uplt.subplots(proj="cyl", backend="cartopy")
    ax[0]._toggle_gridliner_labels(labelleft=False, labelbottom=False)
    gl = ax[0].gridlines_major

    assert gl.left_labels == False
    assert gl.right_labels == False
    assert gl.top_labels == False
    assert gl.bottom_labels == False
    ax[0]._toggle_gridliner_labels(labeltop=True)
    assert gl.top_labels == True
    uplt.close(fig)

    # Basemap backend
    fig, ax = uplt.subplots(proj="cyl", backend="basemap")
    ax.format(land=True, labels="both")  # need this otherwise no labels are printed
    ax[0]._toggle_gridliner_labels(
        labelleft=False,
        labelbottom=False,
        labelright=False,
        labeltop=False,
    )
    gl = ax[0].gridlines_major

    # All label are off
    for gli in gl:
        for _, (line, labels) in gli.items():
            for label in labels:
                assert label.get_visible() == False

    # Should be off
    ax[0]._toggle_gridliner_labels(labeltop=True)
    # Gridliner labels are not added for the top (and I guess right for GeoAxes).
    # Need to figure out how this is set in matplotlib
    dir_labels = ax[0]._get_gridliner_labels(
        left=True, right=True, top=True, bottom=True
    )
    for dir, labels in dir_labels.items():
        expectation = False
        if dir in "top":
            expectation = True
        for label in labels:
            assert label.get_visible() == expectation
    uplt.close(fig)


def test_sharing_geo_limits():
    """
    Test that we can share limits on GeoAxes
    """
    fig, ax = uplt.subplots(
        ncols=2,
        proj="cyl",
        share=False,
    )
    expectation = dict(
        lonlim=(-10, 10),
        latlim=(-13, 15),
    )
    ax.format(land=True)
    ax[0].format(**expectation)

    before_lon = ax[1]._lonaxis.get_view_interval()
    before_lat = ax[1]._lataxis.get_view_interval()

    # Need to set this otherwise will be skipped
    fig._sharey = 3
    ax[0]._sharey_setup(ax[1])  # manually call setup
    ax[0]._sharey_limits(ax[1])  # manually call sharing limits
    # Limits should now be shored for lat but not for lon
    after_lat = ax[1]._lataxis.get_view_interval()

    # We are sharing y which is the latitude axis
    assert all([np.allclose(i, j) for i, j in zip(expectation["latlim"], after_lat)])
    # We are not sharing longitude yet
    assert all(
        [
            not np.allclose(i, j)
            for i, j in zip(expectation["lonlim"], ax[1]._lonaxis.get_view_interval())
        ]
    )

    ax[0]._sharex_setup(ax[1])
    ax[0]._sharex_limits(ax[1])
    after_lon = ax[1]._lonaxis.get_view_interval()

    assert all([not np.allclose(i, j) for i, j in zip(before_lon, after_lon)])
    assert all([np.allclose(i, j) for i, j in zip(after_lon, expectation["lonlim"])])
    uplt.close(fig)


def test_copy_locator_props():
    """
    When sharing axes the locator properties need
    to move as well.
    """

    fig, ax = uplt.subplots(ncols=2, proj="cyl", share=0)

    g1 = ax[0]._lonaxis
    g2 = ax[1]._lonaxis
    props = [
        "isDefault_majloc",
        "isDefault_minloc",
        "isDefault_majfmt",
    ]
    for prop in props:
        assert hasattr(g1, prop)
        assert hasattr(g2, prop)
        setattr(g1, prop, False)
        setattr(g2, prop, True)

    # The copy happens when the properties between g1 and g2 differ. Note this copies from g1 to g2.
    g1._copy_locator_properties(g2)
    for prop in props:
        assert getattr(g1, prop) == False
        assert getattr(g1, prop) == getattr(g2, prop)


def test_turn_off_tick_labels_basemap():
    """
    Check if we can toggle the labels off for GeoAxes
    with a basemap backend.
    """
    fig, ax = uplt.subplots(proj="cyl", backend="basemap")
    ax.format(labels="both")
    locators = ax[0].gridlines_major

    def test_if_labels_are(is_on, locator):
        from matplotlib import text as mtext

        for loc, objects in locator.items():
            for object in objects:
                if isinstance(object, list) and len(objects) > 0:
                    object = object[0]
                if isinstance(object, mtext.Text):
                    assert object.get_visible() == is_on

    # Check if the labels are on
    for locator in locators:
        test_if_labels_are(is_on=True, locator=locator)

    # Turn off both the labels
    for locator in locators:
        ax[0]._turnoff_tick_labels(locator)

    # Check if  are off
    for locator in locators:
        test_if_labels_are(is_on=False, locator=locator)
    uplt.close(fig)


def test_get_gridliner_labels_cartopy():
    from itertools import product

    fig, ax = uplt.subplots(proj="cyl", backend="cartopy")
    ax.format(labels="both")
    bools = [True, False]

    for bottom, top, left, right in product(bools, bools, bools, bools):
        ax[0]._toggle_gridliner_labels(
            labelleft=left,
            labelright=right,
            labeltop=top,
            labelbottom=bottom,
        )
        fig.canvas.draw()  # need draw to retrieve the labels
        labels = ax[0]._get_gridliner_labels(
            bottom=bottom,
            top=top,
            left=left,
            right=right,
        )
        for dir, is_on in zip(
            "bottom top left right".split(), [bottom, top, left, right]
        ):
            if is_on:
                assert len(labels.get(dir, [])) > 0
            else:
                assert len(labels.get(dir, [])) == 0
    uplt.close(fig)


def test_sharing_levels():
    """
    We can share limits or labels.
    We check if we can do both for the GeoAxes.
    """
    # We can share labels, limits, scale or all
    # For labels we share the axis labels but nothing else
    # Limits shares both labels and ticks
    # Scale (= True) will also share the scale
    # All does all the ticks across all plots
    # (not necessarily on same line)
    #
    # Succinctly this means that for
    # - share = 0: no sharing takes place, each
    # axis have their tick labels and data limits are their
    # own
    # - share = 1: x and y labels are shared but nothing else
    # - share = 2: ticks are shared  but still are shown
    # - share = 3: ticks are shared and turned of for the ticks
    # facing towards the "inside"
    # - share = 4: ticks are shared, and the data limits are the same

    x = np.array([0, 10])
    y = np.array([0, 10])
    sharing_levels = [0, 1, 2, 3, 4]
    lonlim = latlim = np.array((-10, 10))

    def assert_views_are_sharing(ax):
        # We are testing a 2x2 grid here
        match ax.number - 1:
            # Note ax.number is idx + 1
            case 0:
                targets = [1, 2]
                sharing_x = [False, True]
                sharing_y = [True, False]
            case 1:
                targets = [0, 3]
                sharing_x = [False, True]
                sharing_y = [True, False]
            case 2:
                targets = [0, 3]
                sharing_x = [True, False]
                sharing_y = [False, True]
            case 3:
                targets = [1, 2]
                sharing_x = [True, False]
                sharing_y = [False, True]
        lonview = ax._lonaxis.get_view_interval()
        latview = ax._lataxis.get_view_interval()
        for target, share_x, share_y in zip(targets, sharing_x, sharing_y):
            other = ax.figure.axes[target]
            target_lon = other._lonaxis.get_view_interval()
            target_lat = other._lataxis.get_view_interval()

            l1 = np.linalg.norm(
                np.asarray(lonview) - np.asarray(target_lon),
            )
            l2 = np.linalg.norm(
                np.asarray(latview) - np.asarray(target_lat),
            )
            level = ax.figure._get_sharing_level()
            if level <= 1:
                share_x = share_y = False
            assert np.allclose(l1, 0) == share_x
            assert np.allclose(l2, 0) == share_y

    for level in sharing_levels:
        fig, ax = uplt.subplots(ncols=2, nrows=2, proj="cyl", share=level)
        ax.format(labels="both")
        for axi in ax:
            axi.format(
                lonlim=lonlim * axi.number,
                latlim=latlim * axi.number,
            )

        fig.canvas.draw()
        for idx, axi in enumerate(ax):
            axi.plot(x * (idx + 1), y * (idx + 1))

        fig.canvas.draw()  # need this to update the labels
        # All the labels should be on
        for axi in ax:
            side_labels = axi._get_gridliner_labels(
                left=True,
                right=True,
                top=True,
                bottom=True,
            )
            s = 0
            for dir, labels in side_labels.items():
                s += any([label.get_visible() for label in labels])

            assert_views_are_sharing(axi)
            # When we share the labels but not the limits,
            # we expect all ticks to be on
            if level == 0:
                assert s == 4
            else:
                assert s == 2
        uplt.close(fig)


@pytest.mark.mpl_image_compare
def test_cartesian_and_geo(rng):
    """
    Test that axis sharing does not prevent
    running Cartesian based plot functions
    """

    fig, ax = uplt.subplots(
        ncols=2,
        proj="cyl",
        share=True,
    )
    original_toggler = ax[0]._toggle_gridliner_labels
    with mock.patch.object(
        ax[0],
        "_toggle_gridliner_labels",
        autospec=True,
        side_effect=original_toggler,
    ) as mocked:
        # Make small range to speed up plotting
        ax.format(land=True, lonlim=(-10, 10), latlim=(-10, 10))
        ax[0].pcolormesh(rng.random((10, 10)))
        ax[1].scatter(*rng.random((2, 100)))
        ax[0]._apply_axis_sharing()
        assert mocked.call_count == 2
    return fig


def test_rasterize_feature():
    fig, ax = uplt.subplots(proj="cyl")
    ax.format(
        land=True,
        landrasterized=True,
        ocean=True,
        oceanrasterized=True,
        rivers=True,
        riversrasterized=True,
        borders=True,
        bordersrasterized=True,
    )
    for feature in "land ocean rivers borders".split():
        feat = getattr(ax[0], f"_{feature}_feature")
        assert feat._kwargs["rasterized"]
    uplt.close(fig)


def test_check_tricontourf():
    """
    Ensure that tricontour functions are getting
    the transform for GeoAxes.
    """
    import cartopy.crs as ccrs

    lon0 = 90
    lon = np.linspace(-180, 180, 10)
    lat = np.linspace(-90, 90, 10)
    lon2d, lat2d = np.meshgrid(lon, lat)

    data = np.sin(3 * np.radians(lat2d)) * np.cos(2 * np.radians(lon2d))
    # Place a box with constant values in order to have a visual reference
    mask_box = (lon2d >= 0) & (lon2d <= 20) & (lat2d >= 0) & (lat2d <= 20)
    data[mask_box] = 1.5

    lon, lat, data = map(np.ravel, (lon2d, lat2d, data))

    fig, ax = uplt.subplots(proj="cyl", proj_kw={"lon0": lon0})
    original_func = ax[0]._call_native
    with mock.patch.object(
        ax[0],
        "_call_native",
        autospec=True,
        side_effect=original_func,
    ) as mocked:
        for func in "tricontour tricontourf".split():
            getattr(ax[0], func)(lon, lat, data)
        assert "transform" in mocked.call_args.kwargs
        assert isinstance(mocked.call_args.kwargs["transform"], ccrs.PlateCarree)
    uplt.close(fig)


def test_panels_geo():
    fig, ax = uplt.subplots(proj="cyl")
    ax.format(labels=True)
    for dir in "top bottom right left".split():
        pax = ax.panel_axes(dir)
        match dir:
            case "top":
                assert len(pax.get_xticklabels()) > 0
                assert len(pax.get_yticklabels()) > 0
            case "bottom":
                assert len(pax.get_xticklabels()) > 0
                assert len(pax.get_yticklabels()) > 0
            case "left":
                assert len(pax.get_xticklabels()) > 0
                assert len(pax.get_yticklabels()) > 0
            case "right":
                assert len(pax.get_xticklabels()) > 0
                assert len(pax.get_yticklabels()) > 0


@pytest.mark.mpl_image_compare
def test_geo_with_panels(rng):
    """
    We are allowed to add panels in GeoPlots
    """
    # Define coordinates
    lat = np.linspace(-90, 90, 180)
    lon = np.linspace(-180, 180, 360)
    time = np.arange(2000, 2005)
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    # Zoomed region elevation (Asia region)
    lat_zoom = np.linspace(0, 60, 60)
    lon_zoom = np.linspace(60, 180, 120)
    lz, lz_grid = np.meshgrid(lon_zoom, lat_zoom)

    elevation = (
        2000 * np.exp(-((lz - 90) ** 2 + (lz_grid - 30) ** 2) / 400)
        + 1000 * np.exp(-((lz - 120) ** 2 + (lz_grid - 45) ** 2) / 225)
        + rng.normal(0, 100, lz.shape)
    )
    elevation = np.clip(elevation, 0, 4000)

    fig, ax = uplt.subplots(nrows=2, proj="cyl")
    pax = ax[0].panel("r")
    pax.barh(lat_zoom, elevation.sum(axis=1))
    pax = ax[1].panel("r")
    pax.barh(lat_zoom - 30, elevation.sum(axis=1))
    ax[0].pcolormesh(
        lon_zoom,
        lat_zoom,
        elevation,
        cmap="bilbao",
        colorbar="t",
        colorbar_kw=dict(
            align="l",
            length=0.5,
        ),
    )
    ax[1].pcolormesh(
        lon_zoom,
        lat_zoom - 30,
        elevation,
        cmap="glacial",
        colorbar="t",
        colorbar_kw=dict(
            align="r",
            length=0.5,
        ),
    )
    ax.format(oceancolor="blue", coast=True)
    return fig


@pytest.mark.mpl_image_compare
def test_inset_axes_geographic():
    fig, ax = uplt.subplots(proj="cyl")
    ax.format(labels=True)

    e = [126, 30, 8.8, 10]
    ix = ax.inset_axes(
        e,
        zoom=True,
        zoom_kw={"fc": "r", "ec": "b"},
        transform="data",
    )
    ix.format(
        lonlim=(100, 110),
        latlim=(20, 30),
    )
    return fig


def test_tick_toggler():
    fig, ax = uplt.subplots(proj="cyl")
    for pos in "left right top bottom".split():
        if pos in "left right".split():
            ax.format(latlabels=pos)
        else:
            ax.format(lonlabels=pos)
        ax.set_title(f"Toggle {pos} labels")
        # Check if the labels are on
        # For cartopy backend labelleft can contain
        # False or x or y
        label = f"label{pos}"
        assert ax[0]._is_ticklabel_on(label) != False
        ax[0]._toggle_gridliner_labels(**{label: False})
        assert ax[0]._is_ticklabel_on(label) != True
    uplt.close(fig)


@pytest.mark.mpl_image_compare
def test_sharing_cartopy_with_colorbar(rng):

    def are_labels_on(ax, which=("top", "bottom", "right", "left")) -> tuple[bool]:
        gl = ax.gridlines_major

        on = [False, False, False, False]
        for idx, labeler in enumerate(which):
            if getattr(gl, f"{labeler}_labels"):
                on[idx] = True
        return on

    fig, ax = uplt.subplots(
        ncols=3,
        nrows=3,
        proj="cyl",
        share="all",
    )

    data = rng.random((10, 10))
    h = ax.imshow(data)[0]
    ax.format(land=True, labels="both")  # need this otherwise no labels are printed
    fig.colorbar(h, loc="r")

    expectations = (
        [True, False, False, True],
        [True, False, False, False],
        [True, False, True, False],
        [False, False, False, True],
        [False, False, False, False],
        [False, False, True, False],
        [False, True, False, True],
        [False, True, False, False],
        [False, True, True, False],
    )
    for axi in ax:
        state = are_labels_on(axi)
        expectation = expectations[axi.number - 1]
        for i, j in zip(state, expectation):
            assert i == j
    return fig


def test_consistent_range():
    """
    Check if the extent of the axes is consistent
    after setting ticklen. Ticklen uses a MaxNlocator which
    changes the extent of the axes -- we are resetting
    it now explicitly.
    """

    lonlim = np.array((10, 20))
    latlim = np.array((10, 20))
    fig, ax = uplt.subplots(ncols=2, proj="cyl", share=False)

    ax.format(
        lonlim=(10, 20),
        latlim=latlim,
        lonlines=2,
        latlines=2,
        lonlabels="both",
        latlabels="both",
    )
    # Now change ticklen of ax[1], cause extent change
    ax[1].format(ticklen=1)
    for a in ax:
        lonview = np.array(a._lonaxis.get_view_interval())
        latview = np.array(a._lataxis.get_view_interval())

        assert np.allclose(lonview, lonlim)
        assert np.allclose(latview, latlim)


@pytest.mark.mpl_image_compare
def test_dms_used_for_mercator():
    """
    Test that DMS is used for Mercator projection
    """
    limit = (0.6, 113.25)
    fig, ax = uplt.subplots(ncols=2, proj=("cyl", "merc"), share=0)
    ax.format(land=True, labels=True, lonlocator=limit)
    ax.format(land=True, labels=True, lonlocator=limit)
    import matplotlib.ticker as mticker

    expectations = (
        "0°36′E",
        "113°15′E",
    )

    for expectation, tick in zip(expectations, limit):
        a = ax[0].gridlines_major.xformatter(tick)
        b = ax[1].gridlines_major.xformatter(tick)
        assert a == expectation
        assert b == expectation
    return fig


@pytest.mark.mpl_image_compare
def test_imshow_with_and_without_transform(rng):
    data = rng.random((100, 100))
    fig, ax = uplt.subplots(ncols=3, proj="lcc", share=0)
    ax.format(land=True, labels=True)
    ax[:2].format(
        latlim=(-10, 10),
        lonlim=(-10, 10),
    )
    ax[0].imshow(data, transform=ax[0].projection)
    ax[1].imshow(data, transform=None)
    ax[2].imshow(data, transform=uplt.axes.geo.ccrs.PlateCarree())
    ax.format(title=["LCC", "No transform", "PlateCarree"])
    return fig


@pytest.mark.mpl_image_compare
def test_grid_indexing_formatting(rng):
    """
    Check if subplotgrid is correctly selecting
    the subplots based on non-shared axis formatting
    """
    # See https://github.com/Ultraplot/UltraPlot/issues/356
    lon = np.arange(0, 360, 10)
    lat = np.arange(-60, 60 + 1, 10)
    data = rng.random((len(lat), len(lon)))

    fig, axs = uplt.subplots(nrows=3, ncols=2, proj="cyl", share=0)
    axs.format(coast=True)

    for ax in axs:
        m = ax.pcolor(lon, lat, data)
        ax.colorbar(m)

    axs[-1, :].format(lonlabels=True)
    axs[:, 0].format(latlabels=True)
    return fig
