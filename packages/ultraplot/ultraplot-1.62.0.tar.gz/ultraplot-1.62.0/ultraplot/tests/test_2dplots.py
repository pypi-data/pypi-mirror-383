#!/usr/bin/env python3
"""
Test 2D plotting overrides.
"""
import numpy as np
import pytest
import xarray as xr

import ultraplot as uplt, warnings


@pytest.mark.skip("not sure what this does")
@pytest.mark.mpl_image_compare
def test_colormap_vcenter(rng):
    """
    Test colormap vcenter.
    """
    fig, axs = uplt.subplots(ncols=3)
    data = 10 * rng.random((10, 10)) - 3
    axs[0].pcolor(data, vcenter=0)
    axs[1].pcolor(data, vcenter=1)
    axs[2].pcolor(data, vcenter=2)
    return fig


@pytest.mark.mpl_image_compare
def test_auto_diverging1(rng):
    """
    Test that auto diverging works.
    """
    # Test with basic data
    fig = uplt.figure()
    # fig.format(collabels=('Auto sequential', 'Auto diverging'), suptitle='Default')
    ax = fig.subplot(121)
    ax.pcolor(rng.random((10, 10)) * 5, colorbar="b")
    ax = fig.subplot(122)
    ax.pcolor(rng.random((10, 10)) * 5 - 3.5, colorbar="b")
    fig.format(toplabels=("Sequential", "Diverging"))
    return fig


@pytest.mark.skip("Not sure what this does")
@pytest.mark.mpl_image_compare
def test_autodiverging2(rng):
    """Test whether automatic diverging cmap is disabled when specified."""
    fig, axs = uplt.subplots(ncols=3)
    data = 5 * rng.random((10, 10))
    axs[0].pcolor(data, vcenter=0, colorbar="b")  # otherwise should be disabled
    axs[1].pcolor(data, vcenter=1.5, colorbar="b")
    axs[2].pcolor(data, vcenter=4, colorbar="b", symmetric=True)
    return fig


@pytest.mark.mpl_image_compare
def test_autodiverging3(rng):
    """
    Test 2D colors.
    """
    fig, axs = uplt.subplots(ncols=2, nrows=2, refwidth=2)
    cmap = uplt.Colormap(
        ("red7", "red3", "red1", "blue1", "blue3", "blue7"), listmode="discrete"
    )  # noqa: E501
    data1 = 10 * rng.random((10, 10))
    data2 = data1 - 2
    for i, cmap in enumerate(("RdBu_r", cmap)):
        for j, data in enumerate((data1, data2)):
            cmap = uplt.Colormap(uplt.Colormap(cmap))
            axs[i, j].pcolormesh(data, cmap=cmap, colorbar="b")
    return fig


@pytest.mark.mpl_image_compare
def test_autodiverging4(rng):
    """Test disabling auto diverging with keyword arguments."""
    fig, axs = uplt.subplots(ncols=3)
    data = rng.random((5, 5)) * 10 - 5
    for i, ax in enumerate(axs[:2]):
        ax.pcolor(data, sequential=bool(i), colorbar="b")
    axs[2].pcolor(data, diverging=False, colorbar="b")  # should have same effect
    return fig


@pytest.mark.mpl_image_compare
def test_autodiverging5(rng):
    """Test auto diverging enabled and disabled."""
    fig, axs = uplt.subplots(ncols=2)
    data = rng.random((5, 5)) * 10 + 2
    for ax, norm in zip(axs, (None, "div")):
        ax.pcolor(data, norm=norm, colorbar="b")
    return fig


@pytest.mark.mpl_image_compare
def test_colormap_mode(rng):
    """
    Test auto extending, auto discrete. Should issue warnings.
    """
    fig, axs = uplt.subplots(ncols=2, nrows=2, share=False)
    axs[0].pcolor(rng.random((5, 5)) % 0.3, extend="both", cyclic=True, colorbar="b")
    with pytest.warns(uplt.warnings.UltraPlotWarning):
        axs[1].pcolor(rng.random((5, 5)), sequential=True, diverging=True, colorbar="b")

    with pytest.warns(uplt.warnings.UltraPlotWarning):
        axs[2].pcolor(
            rng.random((5, 5)), discrete=False, qualitative=True, colorbar="b"
        )
    with uplt.rc.context({"cmap.discrete": False}):  # should be ignored below
        axs[3].contourf(rng.random((5, 5)), colorbar="b")
    return fig


@pytest.mark.mpl_image_compare
def test_contour_labels(rng):
    """
    Test contour labels. We use a separate `contour` object when adding labels to
    filled contours or else weird stuff happens (see below). We could just modify
    filled contour edges when not adding labels but that would be inconsistent with
    behavior when labels are active.
    """
    data = rng.random((5, 5)) * 10 - 5
    fig, axs = uplt.subplots(ncols=2)
    ax = axs[0]
    ax.contourf(
        data,
        edgecolor="k",
        linewidth=1.5,
        labels=True,
        labels_kw={"color": "k", "size": "large"},
    )
    ax = axs[1]
    m = ax.contourf(data)
    ax.clabel(m, colors="black", fontsize="large")  # looks fine without this

    import matplotlib.patheffects as pe

    m.set_path_effects([pe.Stroke(linewidth=1.5, foreground="k"), pe.Normal()])
    return fig


@pytest.mark.mpl_image_compare
def test_contour_negative(rng):
    """
    Ensure `cmap.monochrome` properly assigned.
    """
    fig = uplt.figure(share=False)
    ax = fig.subplot(131)
    data = rng.random((10, 10)) * 10 - 5
    ax.contour(data, color="k")
    ax = fig.subplot(132)
    ax.tricontour(*(rng.random((3, 20)) * 10 - 5), color="k")
    ax = fig.subplot(133)
    ax.contour(data, cmap=["black"])  # fails but that's ok
    return fig


@pytest.mark.mpl_image_compare
def test_contour_single():
    """
    Test whether single contour works.
    """
    da = xr.DataArray(
        np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]), dims=["y", "x"]
    )
    fig, ax = uplt.subplots()
    ax.contour(da, levels=[5.0], color="r")
    return fig


@pytest.mark.mpl_image_compare
def test_edge_fix(rng):
    """
    Test whether level extension works with negative and positive levels.
    """
    # Test whether ignored for bar plots
    fig, axs = uplt.subplots(ncols=2, nrows=2, share=False)
    axs[0].bar(
        rng.random(10) * 10 - 5,
        width=1,
        negpos=True,
    )
    axs[1].area(rng.random((5, 3)), stack=True)

    # Test whether ignored for transparent colorbars
    data = rng.random((10, 10))
    cmap = "magma"
    fig, axs = uplt.subplots(nrows=3, ncols=2, refwidth=2.5, share=False)
    for i, iaxs in enumerate((axs[:2], axs[2:4])):
        if i == 0:
            cmap = uplt.Colormap("magma", alpha=0.5)
            alpha = None
            iaxs.format(title="Colormap alpha")
        else:
            cmap = "magma"
            alpha = 0.5
            iaxs.format(title="Single alpha")
        iaxs[0].contourf(data, cmap=cmap, colorbar="b", alpha=alpha)
        iaxs[1].pcolormesh(data, cmap=cmap, colorbar="b", alpha=alpha)
    axs[4].bar(data[:3, :3], alpha=0.5)
    axs[5].area(data[:3, :3], alpha=0.5, stack=True)
    return fig


@pytest.mark.mpl_image_compare
def test_flow_functions(rng):
    """
    These are seldom used and missing from documentation. Be careful
    not to break anything basic.
    """
    fig, axs = uplt.subplots(ncols=2)
    ax = axs[0]
    for _ in range(2):
        ax.streamplot(rng.random((10, 10)), 5 * rng.random((10, 10)), label="label")

    ax = axs[0]
    ax.quiver(
        rng.random((10, 10)),
        5 * rng.random((10, 10)),
        c=rng.random((10, 10)),
        label="label",
    )
    ax = axs[1]
    ax.quiver(rng.random(10), rng.random(10), label="single")
    return fig


@pytest.mark.mpl_image_compare
def test_gray_adjustment(rng):
    """
    Test gray adjustments when creating segmented colormaps.
    """
    fig, ax = uplt.subplots()
    data = rng.random((5, 5)) * 10 - 5
    cmap = uplt.Colormap(["blue", "grey3", "red"])
    ax.pcolor(data, cmap=cmap, colorbar="b")
    return fig


@pytest.mark.mpl_image_compare
def test_ignore_message(rng):
    """
    Test various ignored argument warnings.
    """
    warning = uplt.internals.UltraPlotWarning
    fig, axs = uplt.subplots(ncols=2, nrows=2)
    with pytest.warns(warning):
        axs[0].contour(rng.random((5, 5)) * 10, levels=uplt.arange(10), symmetric=True)
    with pytest.warns(warning):
        axs[1].contourf(
            rng.random((10, 10)),
            levels=np.linspace(0, 1, 10),
            locator=5,
            locator_kw={},
        )
    with pytest.warns(warning):
        axs[2].contourf(
            rng.random((10, 10)),
            levels=uplt.arange(0, 1, 0.2),
            vmin=0,
            vmax=2,
            locator=3,
            colorbar="b",
        )
    with pytest.warns(warning):
        axs[3].hexbin(
            rng.random(1000),
            rng.random(1000),
            levels=uplt.arange(0, 20),
            gridsize=10,
            locator=2,
            colorbar="b",
            cmap="blues",
        )
    return fig


@pytest.mark.mpl_image_compare
def test_levels_with_vmin_vmax(rng):
    """
    Make sure `vmin` and `vmax` go into level generation algorithm.
    """
    # Sample data
    x = y = np.array([-10, -5, 0, 5, 10])
    data = rng.random((y.size, x.size))

    # Figure
    fig = uplt.figure(refwidth=2.3, share=False)
    axs = fig.subplots()
    m = axs.pcolormesh(x, y, data, vmax=1.35123)
    axs.colorbar([m], loc="r")
    return fig


@pytest.mark.mpl_image_compare
def test_level_restriction(rng):
    """
    Test `negative`, `positive`, and `symmetric` with and without discrete.
    """
    fig, axs = uplt.subplots(ncols=3, nrows=2)
    data = 20 * rng.random((10, 10)) - 5
    keys = ("negative", "positive", "symmetric")
    for i, grp in enumerate((axs[:3], axs[3:])):
        for j, ax in enumerate(grp):
            kw = {keys[j]: True, "discrete": bool(1 - i)}
            ax.pcolor(data, **kw, colorbar="b")
    return fig


@pytest.mark.mpl_image_compare
def test_qualitative_colormaps_1(rng):
    """
    Test both `colors` and `cmap` input and ensure extend setting is used for
    extreme only if unset.
    """
    fig, axs = uplt.subplots(ncols=2)
    data = rng.random((5, 5))
    colors = uplt.get_colors("set3")
    for ax, extend in zip(axs, ("both", "neither")):
        ax.pcolor(data, extend=extend, colors=colors, colorbar="b")
    return fig


@pytest.mark.mpl_image_compare
def test_qualitative_colormaps_2(rng):
    fig, axs = uplt.subplots(ncols=2)
    data = rng.random((5, 5))
    cmap = uplt.Colormap("set3")
    cmap.set_under("black")  # does not overwrite
    for ax, extend in zip(axs, ("both", "neither")):
        ax.pcolor(data, extend=extend, cmap=cmap, colorbar="b")
    return fig


@pytest.mark.mpl_image_compare
def test_segmented_norm(rng):
    """
    Test segmented norm with non-discrete levels.
    """
    fig, ax = uplt.subplots()
    ax.pcolor(
        rng.random((5, 5)) * 10,
        discrete=False,
        norm="segmented",
        norm_kw={"levels": [0, 2, 10]},
        colorbar="b",
    )
    return fig


@pytest.mark.mpl_image_compare
def test_triangular_functions(rng):
    """
    Test triangular functions. Here there is no remotely sensible way to infer
    """
    fig, ax = uplt.subplots()
    N = 30
    y = rng.random(N) * 20
    x = rng.random(N) * 50
    da = xr.DataArray(rng.random(N), dims=("x",), coords={"x": x, "y": ("x", y)})
    ax.tricontour(da.x, da.y, da, labels=True)
    return fig


@pytest.mark.mpl_image_compare
def test_colorbar_extends(rng):
    """
    Test all the possible extends
    """
    # Ensure that the colorbars are not showing artifacts on the ticks. In the past extend != neither showed ghosting on the ticks. This occured after a manual draw after the colorbar was created.
    fig, ax = uplt.subplots(nrows=2, ncols=2, share=False)
    data = rng.random((20, 20))
    levels = np.linspace(0, 1, 11)
    extends = ["neither", "both", "min", "max"]
    for extend, axi in zip(extends, ax):
        m = axi.contourf(data, levels=levels, extend=extend)
        axi.colorbar(m)
    return fig
