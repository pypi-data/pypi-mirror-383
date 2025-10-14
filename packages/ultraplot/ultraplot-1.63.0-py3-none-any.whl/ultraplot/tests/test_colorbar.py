#!/usr/bin/env python3
"""
Test colorbars.
"""
import numpy as np
import pytest
import ultraplot as uplt
from itertools import product


@pytest.mark.mpl_image_compare
def test_outer_align():
    """
    Test various align options.
    """
    fig, ax = uplt.subplots()
    ax.plot(np.empty((0, 4)), labels=list("abcd"))
    ax.legend(loc="bottom", align="right", ncol=2)
    ax.legend(loc="left", align="bottom", ncol=1)
    ax.colorbar(
        "magma",
        loc="top",
        ticklen=0,
        tickloc="bottom",
        align="left",
        shrink=0.5,
        label="Title",
        extend="both",
        labelloc="top",
        labelweight="bold",
    )
    ax.colorbar(
        "magma",
        loc="r",
        align="top",
        shrink=0.5,
        label="label",
        extend="both",
        labelrotation=90,
    )
    ax.colorbar(
        "magma", loc="right", extend="both", label="test extensions", labelrotation=90
    )
    fig.suptitle("Align demo", va="bottom")
    return fig


@pytest.mark.mpl_image_compare
def test_colorbar_ticks():
    """
    Test ticks modification.
    """
    fig, axs = uplt.subplots(ncols=2)
    ax = axs[0]
    ax.colorbar("magma", loc="bottom", ticklen=10, linewidth=3, tickminor=True)
    ax = axs[1]
    ax.colorbar(
        "magma", loc="bottom", ticklen=10, linewidth=3, tickwidth=1.5, tickminor=True
    )
    return fig


@pytest.mark.mpl_image_compare
def test_discrete_ticks(rng):
    """
    Test `DiscreteLocator`.
    """
    levels = uplt.arange(0, 2, 0.1)
    data = rng.random((5, 5)) * 2
    fig, axs = uplt.subplots(share=False, ncols=2, nrows=2, refwidth=2)
    for i, ax in enumerate(axs):
        cmd = ax.contourf if i // 2 == 0 else ax.pcolormesh
        m = cmd(data, levels=levels, extend="both")
        ax.colorbar(m, loc="t" if i // 2 == 0 else "b")
        ax.colorbar(m, loc="l" if i % 2 == 0 else "r")
    return fig


@pytest.mark.mpl_image_compare
def test_discrete_vs_fixed(rng):
    """
    Test `DiscreteLocator` for numeric on-the-fly
    mappable ticks and `FixedLocator` otherwise.
    """
    fig, axs = uplt.subplots(ncols=2, nrows=3, refwidth=1.3, share=False)
    axs[0].plot(rng.random((10, 5)), labels=list("xyzpq"), colorbar="b")  # fixed
    axs[1].plot(rng.random((10, 5)), labels=np.arange(5), colorbar="b")  # discrete
    axs[2].contourf(
        rng.random((10, 10)),
        colorbar="b",
        colorbar_kw={"ticklabels": list("xyzpq")},  # fixed
    )
    axs[3].contourf(rng.random((10, 10)), colorbar="b")  # discrete
    axs[4].pcolormesh(
        rng.random((10, 10)) * 20, colorbar="b", levels=[0, 2, 4, 6, 8, 10, 15, 20]
    )  # fixed
    axs[5].pcolormesh(
        rng.random((10, 10)) * 20, colorbar="b", levels=uplt.arange(0, 20, 2)
    )  # discrete
    return fig


@pytest.mark.mpl_image_compare
def test_uneven_levels(rng):
    """
    Test even and uneven levels with discrete cmap. Ensure minor ticks are disabled.
    """
    N = 20
    data = np.cumsum(rng.random((N, N)), axis=1) * 12
    colors = [
        "white",
        "indigo1",
        "indigo3",
        "indigo5",
        "indigo7",
        "indigo9",
        "yellow1",
        "yellow3",
        "yellow5",
        "yellow7",
        "yellow9",
        "violet1",
        "violet3",
    ]
    levels_even = uplt.arange(1, 12, 1)
    levels_uneven = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.75, 4.5, 6.0, 7.5, 9.0, 12.0]
    fig, axs = uplt.subplots(ncols=2, refwidth=3.0)
    axs[0].pcolor(
        data, levels=levels_uneven, colors=colors, colorbar="r", extend="both"
    )
    axs[1].pcolor(data, levels=levels_even, colors=colors, colorbar="r", extend="both")
    return fig


@pytest.mark.mpl_image_compare
def test_on_the_fly_mappable(rng):
    """
    Test on-the-fly mappable generation.
    """
    fig, axs = uplt.subplots(ncols=2, nrows=3, space=3)
    axs.format(aspect=0.5)
    axs[0].colorbar("magma", vmin=None, vmax=100, values=[0, 1, 2, 3, 4], loc="bottom")
    axs[1].colorbar("magma", vmin=None, vmax=100, loc="bottom")
    axs[2].colorbar("colorblind", vmin=None, vmax=None, values=[0, 1, 2], loc="bottom")
    axs[3].colorbar("colorblind", vmin=None, vmax=None, loc="bottom")
    axs[4].colorbar(["r", "b", "g", "k", "w"], values=[0, 1, 2], loc="b")
    axs[5].colorbar(["r", "b", "g", "k", "w"], loc="bottom")

    # Passing labels to plot function.
    fig, ax = uplt.subplots()
    ax.scatter(rng.random((10, 4)), labels=["foo", "bar", "baz", "xyz"], colorbar="b")

    # Passing string value lists. This helps complete the analogy with legend 'labels'.
    fig, ax = uplt.subplots()
    hs = ax.line(rng.random((20, 5)))
    ax.colorbar(hs, loc="b", values=["abc", "def", "ghi", "pqr", "xyz"])
    return fig


@pytest.mark.mpl_image_compare
def test_inset_colorbars(rng):
    """
    Test basic functionality.
    """
    # Simple example
    fig, ax = uplt.subplots()
    ax.colorbar("magma", loc="ul")

    # Colorbars from lines
    fig = uplt.figure(share=False, refwidth=2)
    ax = fig.subplot(121)
    data = 1 + (rng.random((12, 10)) - 0.45).cumsum(axis=0)
    cycle = uplt.Cycle("algae")
    hs = ax.line(
        data,
        lw=4,
        cycle=cycle,
        colorbar="lr",
        colorbar_kw={"length": "8em", "label": "line colorbar"},
    )
    ax.colorbar(hs, loc="t", values=np.arange(0, 10), label="line colorbar", ticks=2)

    # Colorbars from a mappable
    ax = fig.subplot(122)
    m = ax.contourf(data.T, extend="both", cmap="algae", levels=uplt.arange(0, 3, 0.5))
    fig.colorbar(
        m,
        loc="r",
        length=1,  # length is relative
        label="interior ticks",
        tickloc="left",
    )
    ax.colorbar(
        m,
        loc="ul",
        length=6,  # length is em widths
        label="inset colorbar",
        tickminor=True,
        alpha=0.5,
    )
    fig.format(
        suptitle="Colorbar formatting demo",
        xlabel="xlabel",
        ylabel="ylabel",
        titleabove=False,
    )
    return fig


@pytest.mark.skip("not sure what this does")
@pytest.mark.mpl_image_compare
def test_segmented_norm_center(rng):
    """
    Test various align options.
    """
    fig, ax = uplt.subplots()
    cmap = uplt.Colormap("NegPos", cut=0.1)
    data = rng.random((10, 10)) * 10 - 2
    levels = [-4, -3, -2, -1, 0, 1, 2, 4, 8, 16, 32, 64, 128]
    norm = uplt.SegmentedNorm(levels, vcenter=0, fair=1)
    ax.pcolormesh(data, levels=levels, norm=norm, cmap=cmap, colorbar="b")
    return fig


@pytest.mark.mpl_image_compare
def test_segmented_norm_ticks(rng):
    """
    Ensure segmented norm ticks show up in center when `values` are passed.
    """
    fig, ax = uplt.subplots()
    data = rng.random((10, 10)) * 10
    values = (1, 5, 5.5, 6, 10)
    ax.contourf(
        data,
        values=values,
        colorbar="ll",
        colorbar_kw={"tickminor": True, "minorlocator": np.arange(-20, 20, 0.5)},
    )
    return fig


@pytest.mark.mpl_image_compare
def test_reversed_levels(rng):
    """
    Test negative levels with a discrete norm and segmented norm.
    """
    fig, axs = uplt.subplots(ncols=4, nrows=2, refwidth=1.8)
    data = rng.random((20, 20)).cumsum(axis=0)
    i = 0
    for stride in (1, -1):
        for key in ("levels", "values"):
            for levels in (
                np.arange(0, 15, 1),  # with Normalizer
                [0, 1, 2, 5, 10, 15],  # with LinearSegmentedNorm
            ):
                ax = axs[i]
                kw = {key: levels[::stride]}
                ax.pcolormesh(data, colorbar="b", **kw)
                i += 1
    return fig


@pytest.mark.mpl_image_compare
def test_minor_override(rng):
    """Test minor ticks override."""
    # Setting a custom minor tick should override the settings. Here we set the ticks to 1 and the minorticks to half that. We then check that the minor ticks are set correctly
    data = rng.random((10, 10))
    left, right, minor, n = 0, 1, 0.05, 11
    levels = np.linspace(left, right, n)
    fig, ax = uplt.subplots()
    m = ax.pcolormesh(data, colorbar="b", levels=levels)
    cax = ax.colorbar(m, minorticks=minor)
    assert np.allclose(
        cax.minorlocator.tick_values(left, right),
        np.linspace(left - minor, right + minor, n * 2 + 1),
    )
    return fig


@pytest.mark.mpl_image_compare
def test_draw_edges(rng):
    data = rng.random((10, 10))
    fig, ax = uplt.subplots(ncols=2)
    for axi, drawedges in zip(ax, [True, False]):
        h = axi.pcolor(data, discrete=True)
        axi.colorbar(h, drawedges=drawedges)
        axi.set_title(f"{drawedges=}")
    return fig


@pytest.mark.parametrize("loc", ["top", "bottom", "left", "right"])
def test_label_placement_colorbar(rng, loc):
    """
    Ensure that all potential combinations of colorbar
    label placement is possible.
    """
    data = rng.random((10, 10))
    fig, ax = uplt.subplots()
    h = ax.imshow(data)
    ax.colorbar(h, loc=loc, labelloc=loc)


def test_label_rotation_colorbar():
    """
    Ensure that all potential combinations of colorbar
    label rotation is possible.
    """
    cmap = uplt.colormaps.get_cmap("viridis")
    mylabel = "My Label"
    fig, ax = uplt.subplots()
    cbar = ax.colorbar(cmap, labelloc="top", loc="right", vert=False, labelrotation=23)
    # Get the label Text object
    for which in "xy":
        tmp = getattr(cbar.ax, f"{which}axis").label
        if tmp.get_text() == mylabel:
            label = tmp
            assert label.get_rotation() == 23
            break


@pytest.mark.parametrize(
    ("loc", "labelloc"),
    product(["top", "bottom", "left", "right"], ["top", "bottom", "left", "right"]),
)
def test_auto_labelrotation(loc, labelloc):
    cmap = uplt.colormaps.get_cmap("viridis")
    mylabel = "My Label"

    fig, ax = uplt.subplots()
    cbar = ax.colorbar(cmap, loc=loc, labelloc=labelloc, label=mylabel)

    # Get the label Text object
    for which in "xy":
        tmp = getattr(cbar.ax, f"{which}axis").label
        if tmp.get_text() == mylabel:
            label = tmp
            break

    is_vertical = loc in ("left", "right")
    is_horizontal = not is_vertical

    expected_rotation = 0
    if labelloc == "left":
        expected_rotation = 90
    elif labelloc == "right":
        expected_rotation = 270

    actual_rotation = label.get_rotation()
    ax.set_title(f"loc={loc}, labelloc={labelloc}, rotation={actual_rotation}")
    assert actual_rotation == expected_rotation
    uplt.close(fig)


@pytest.mark.mpl_image_compare
def test_label_placement_fig_colorbar2():
    """
    Ensure that all potential combinations of colorbar
    label placement is possible.
    """
    cmap = uplt.Colormap("plasma_r")
    fig, axs = uplt.subplots(nrows=1, ncols=2)
    fig.colorbar(cmap, loc="bottom", label="My Label", labelloc="right")
    return fig


@pytest.mark.parametrize(
    ("labelloc", "cbarloc"),
    product(
        ["bottom", "top", "left", "right"],
        [
            "top",
            "bottom",
            "left",
            "right",
            "upper right",
            "upper left",
            "lower left",
            "lower right",
        ],
    ),
)
def test_colorbar_label_placement(labelloc, cbarloc):
    """
    Ensure that colorbar label placement works correctly.
    """
    cmap = uplt.Colormap("plasma_r")
    title = "My Label"
    fig, ax = uplt.subplots()

    cbar = ax.colorbar(cmap, loc=cbarloc, labelloc=labelloc, title=title)

    x_label = cbar.ax.xaxis.label.get_text()
    y_label = cbar.ax.yaxis.label.get_text()

    assert title in (x_label, y_label), (
        f"Expected label '{title}' not found. "
        f"xaxis label: '{x_label}', yaxis label: '{y_label}', "
        f"labelloc='{labelloc}', cbarloc='{cbarloc}'"
    )

    uplt.close(fig)


@pytest.mark.parametrize(
    ("cbarloc", "invalid_labelloc"),
    product(
        ["top", "bottom", "upper left", "lower right"],
        ["invalid", "diagonal", "center", "middle", 123, "unknown"],
    ),
)
def test_colorbar_invalid_horizontal_label(cbarloc, invalid_labelloc):
    """
    Test error conditions and edge cases for colorbar label placement.
    """
    cmap = uplt.Colormap("plasma_r")
    title = "Test Label"
    fig, ax = uplt.subplots()

    # Test ValueError cases - invalid labelloc for different colorbar locations

    # Horizontal colorbar location with invalid labelloc
    with pytest.raises(ValueError):
        ax.colorbar(cmap, loc=cbarloc, labelloc=invalid_labelloc, label=title)
    uplt.close(fig)


@pytest.mark.parametrize(
    ("cbarloc", "invalid_labelloc"),
    product(
        ["left", "right", "ll", "ul", "ur", "lr"],
        [
            "invalid",
            "diagonal",
            "center",
            "middle",
            123,
            "unknown",
        ],
    ),
)
def test_colorbar_invalid_vertical_label(cbarloc, invalid_labelloc):
    # Vertical colorbar location with invalid labelloc
    cmap = uplt.Colormap("plasma_r")
    title = "Test Label"
    fig, ax = uplt.subplots()
    with pytest.raises(ValueError):
        ax.colorbar(cmap, loc=cbarloc, labelloc=invalid_labelloc, label=title)
    uplt.close(fig)


@pytest.mark.parametrize(
    "invalid_labelloc", ["fill", "unknown", "custom", "weird_location", 123]
)
def test_colorbar_invalid_fill_label_placement(invalid_labelloc):
    # Fill location with invalid labelloc
    cmap = uplt.Colormap("plasma_r")
    title = "Test Label"
    fig, ax = uplt.subplots()
    with pytest.raises(ValueError):
        ax.colorbar(cmap, loc="fill", labelloc=invalid_labelloc, label=title)


@pytest.mark.parametrize("unknown_loc", ["unknown", "custom", "weird_location", 123])
def test_colorbar_wrong_label_placement_should_raise_error(unknown_loc):
    # Unknown locs should raise errors
    cmap = uplt.Colormap("plasma_r")
    title = "Test Label"
    fig, ax = uplt.subplots()
    with pytest.raises(KeyError):
        cbar = ax.colorbar(cmap, loc=unknown_loc, label=title)


@pytest.mark.parametrize("loc", ["top", "bottom", "left", "right", "fill"])
def test_colorbar_label_no_labelloc(loc):
    cmap = uplt.Colormap("plasma_r")
    title = "Test Label"
    fig, ax = uplt.subplots()
    # None labelloc should always work without error
    cbar = ax.colorbar(cmap, loc=loc, labelloc=None, label=title)

    # Should have the label set somewhere
    label_found = (
        cbar.ax.get_title() == title
        or (
            hasattr(cbar.ax.xaxis.label, "get_text")
            and cbar.ax.xaxis.label.get_text() == title
        )
        or (
            hasattr(cbar.ax.yaxis.label, "get_text")
            and cbar.ax.yaxis.label.get_text() == title
        )
    )
    assert label_found, f"Label not found for loc='{loc}' with labelloc=None"


@pytest.mark.parametrize(
    ("loc", "orientation", "labelloc"),
    product(
        [
            "upper left",
            "upper right",
            "lower left",
            "lower right",
        ],
        ["horizontal", "vertical"],
        ["left", "right", "top", "bottom"],
    ),
)
def test_inset_colorbar_orientation(loc, orientation, labelloc):
    """ """
    cmap = uplt.Colormap("viko")
    fig, ax = uplt.subplots()
    ax.colorbar(
        cmap,
        loc=loc,
        orientation=orientation,
        labellocation=labelloc,
        label="My Label",
    )
    found = False
    for k, v in ax[0]._colorbar_dict.items():
        if loc in k:
            found = True
            break
    assert found, f"Colorbar not found for loc='{loc}' with orientation='{orientation}'"
