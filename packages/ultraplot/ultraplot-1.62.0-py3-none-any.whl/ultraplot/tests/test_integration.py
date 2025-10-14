#!/usr/bin/env python3
"""
Test xarray, pandas, pint, seaborn integration.
"""
import numpy as np, pandas as pd, seaborn as sns
import xarray as xr
import ultraplot as uplt, pytest
import pint


@pytest.mark.mpl_image_compare
def test_pint_quantities(rng):
    """
    Ensure auto-formatting and column iteration both work.
    """
    with uplt.rc.context({"unitformat": "~H"}):
        ureg = pint.UnitRegistry()
        fig, ax = uplt.subplots()
        ax.plot(
            np.arange(10),
            rng.random(10) * ureg.km,
            "C0",
            np.arange(10),
            rng.random(10) * ureg.m * 1e2,
            "C1",
        )
    return fig


@pytest.mark.mpl_image_compare
def test_data_keyword(rng):
    """
    Make sure `data` keywords work properly.
    """
    N = 10
    M = 20
    ds = xr.Dataset(
        {"z": (("x", "y"), rng.random((N, M)))},
        coords={
            "x": ("x", np.arange(N) * 10, {"long_name": "longitude"}),
            "y": ("y", np.arange(M) * 5, {"long_name": "latitude"}),
        },
    )
    fig, ax = uplt.subplots()
    # ax.pcolor('z', data=ds, order='F')
    ax.pcolor(z="z", data=ds, transpose=True)
    ax.format(xformatter="deglat", yformatter="deglon")
    return fig


@pytest.mark.mpl_image_compare
def test_keep_guide_labels(rng):
    """
    Preserve metadata when passing mappables and handles to colorbar and
    legend subsequently.
    """
    fig, ax = uplt.subplots()
    df = pd.DataFrame(rng.random((5, 5)))
    df.name = "variable"
    m = ax.pcolor(df)
    ax.colorbar(m)

    fig, ax = uplt.subplots()
    for k in ("foo", "bar", "baz"):
        s = pd.Series(rng.random(5), index=list("abcde"), name=k)
        ax.plot(
            s,
            legend="ul",
            legend_kw={
                "lw": 5,
                "ew": 2,
                "ec": "r",
                "fc": "w",
                "handle_kw": {"marker": "d"},
            },
        )
    return fig


@pytest.mark.mpl_image_compare
def test_seaborn_swarmplot():
    """
    Test seaborn swarm plots.
    """
    tips = sns.load_dataset("tips")
    fig = uplt.figure(refwidth=3)
    ax = fig.subplot()
    sns.swarmplot(
        ax=ax, x="day", hue="day", y="total_bill", data=tips, palette="cubehelix"
    )
    # fig, ax = uplt.subplots()
    # sns.swarmplot(y=np.random.normal(size=100), ax=ax)
    return fig


@pytest.mark.mpl_image_compare
def test_seaborn_hist(rng):
    """
    Test seaborn histograms.
    """
    fig, axs = uplt.subplots(ncols=2, nrows=2)
    sns.histplot(rng.normal(size=100), ax=axs[0])
    sns.kdeplot(x=rng.random(100), y=rng.random(100), ax=axs[1])
    penguins = sns.load_dataset("penguins")
    sns.histplot(
        data=penguins, x="flipper_length_mm", hue="species", multiple="stack", ax=axs[2]
    )
    sns.kdeplot(
        data=penguins, x="flipper_length_mm", hue="species", multiple="stack", ax=axs[3]
    )
    return fig


@pytest.mark.mpl_image_compare
def test_seaborn_relational():
    """
    Test scatter plots. Disabling seaborn detection creates mismatch between marker
    sizes and legend.
    """
    fig = uplt.figure()
    ax = fig.subplot()
    sns.set_theme(style="white")
    # Load the example mpg dataset
    mpg = sns.load_dataset("mpg")
    # Plot miles per gallon against horsepower with other semantics
    sns.scatterplot(
        x="horsepower",
        y="mpg",
        hue="origin",
        size="weight",
        sizes=(40, 400),
        alpha=0.5,
        palette="muted",
        # legend='bottom',
        # height=6,
        data=mpg,
        ax=ax,
    )
    return fig


@pytest.mark.mpl_image_compare
def test_seaborn_heatmap(rng):
    """
    Test seaborn heatmaps. This should work thanks to backwards compatibility support.
    """
    fig, ax = uplt.subplots()
    sns.heatmap(rng.normal(size=(50, 50)), ax=ax[0])
    return fig
