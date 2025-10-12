# Copyright 2018 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
#
"""
Intra-experiment line graph generation classes for stage{4,5}.
"""

# Core packages
import typing as tp
import logging
import pathlib

# 3rd party packages
import pandas as pd
import holoviews as hv
import matplotlib.pyplot as plt
import bokeh

# Project packages
from sierra.core import config, utils, storage, models
from . import pathset

_logger = logging.getLogger(__name__)


def _ofile_ext(backend: str) -> tp.Optional[str]:
    if backend == "matplotlib":
        return config.kStaticImageType
    elif backend == "bokeh":
        return config.kInteractiveImageType

    return None


def generate(
    paths: pathset.PathSet,
    input_stem: str,
    output_stem: str,
    title: str,
    medium: str,
    backend: str,
    xticks: tp.Optional[tp.List[float]] = None,
    stats: str = "none",
    xlabel: tp.Optional[str] = None,
    ylabel: tp.Optional[str] = None,
    points: tp.Optional[bool] = False,
    large_text: bool = False,
    legend: tp.Optional[tp.List[str]] = None,
    xticklabels: tp.Optional[tp.List[str]] = None,
    cols: tp.Optional[tp.List[str]] = None,
    logyscale: bool = False,
    ext: str = config.kStats["mean"].exts["mean"],
) -> bool:
    """Generate a line graph from a set of columns in a file.

    If the necessary data file does not exist, the graph is not generated.

    If the .stddev file that goes with the .mean does not exist, then no error
    bars are plotted.

    If the .model file that goes with the .mean does not exist, then no model
    predictions are plotted.

    Ideally, model predictions/stddev calculations would be in derived classes,
    but I can't figure out a good way to easily pull that stuff out of here.
    """
    hv.extension(backend)

    input_fpath = paths.input_root / (input_stem + ext)
    output_fpath = paths.output_root / "SLN-{0}.{1}".format(
        output_stem, _ofile_ext(backend)
    )

    if large_text:
        text_size = config.kGraphs["text_size_large"]
    else:
        text_size = config.kGraphs["text_size_small"]

    if not utils.path_exists(input_fpath):
        _logger.debug(
            "Not generating <batchroot>/%s: <batchroot>/%s does not exist",
            output_fpath.relative_to(paths.batchroot),
            input_fpath.relative_to(paths.batchroot),
        )
        return False

    df = storage.df_read(input_fpath, medium)

    # Use xticks if provided, otherwise default to using the dataframe index as
    # the xticks.
    dfcols = df.columns.tolist()
    df["xticks"] = xticks if xticks is not None else df.index.to_list()
    dataset = hv.Dataset(
        # Make index a column so we can use it as kdim
        data=df.reset_index(),
        kdims=["index"],
        vdims=cols if cols else dfcols,
    )

    assert len(df.index) == len(
        df["xticks"]
    ), "Length mismatch between xticks,# data points: {0} vs {1}".format(
        len(df["xticks"]), len(df.index)
    )

    model = _read_models(paths.model_root, input_stem, medium)
    stat_dfs = _read_stats(stats, paths.input_root, input_stem, medium)

    # Plot stats if they have been computed FIRST, so they appear behind the
    # actual data.
    if "conf95" in stats and "stddev" in stat_dfs:
        plot = _plot_stats_stddev(dataset, stat_dfs["stddev"])
        plot *= _plot_selected_cols(dataset, model, legend, points, backend)
    elif "bw" in stats and all(k in stat_dfs.keys() for k in config.kStats["bw"].exts):
        # 2025-10-06 [JRH]: This is a limitation of hv (I think). Manually
        # specifying bw plots around each datapoint on a graph can easily exceed
        # the max # of things that can be in a single overlay.
        _logger.warning("bw statistics not implemented for stacked_line graphs")
        plot = _plot_selected_cols(dataset, model, legend, points, backend)
    else:
        # Plot specified columns from dataframe.
        plot = _plot_selected_cols(dataset, model, legend, points, backend)

    # Let the backend decide # of columns; can override with
    # legend_cols=N in the future if desired.
    plot.opts(legend_position="bottom")

    # Add title
    plot.opts(title=title)

    # Add X,Y labels
    if xlabel is not None:
        plot.opts(xlabel=xlabel)

    if ylabel is not None:
        plot.opts(ylabel=ylabel)

    # Set fontsizes
    plot.opts(
        fontsize={
            "title": text_size["title"],
            "labels": text_size["xyz_label"],
            "ticks": text_size["tick_label"],
            "legend": text_size["legend_label"],
        },
    )

    if logyscale:
        _min = min(dataset[vdim].min() for vdim in dataset.vdims)
        _max = max(dataset[vdim].max() for vdim in dataset.vdims)

        plot.opts(
            logy=True,
            ylim=(
                _min * 0.9,
                _max * 1.1,
            ),
        )

    _save(plot, output_fpath, backend)
    _logger.debug(
        "Graph written to <batchroot>/%s",
        output_fpath.relative_to(paths.batchroot),
    )
    return True


def _save(plot: hv.Overlay, output_fpath: pathlib.Path, backend: str) -> None:
    if backend == "matplotlib":
        hv.save(
            plot.opts(fig_inches=config.kGraphs["base_size"]),
            output_fpath,
            fig=config.kStaticImageType,
            dpi=config.kGraphs["dpi"],
        )
        plt.close("all")
    elif backend == "bokeh":
        fig = hv.render(plot)
        fig.width = int(config.kGraphs["dpi"] * config.kGraphs["base_size"])
        fig.height = int(config.kGraphs["dpi"] * config.kGraphs["base_size"])
        html = bokeh.embed.file_html(fig, resources=bokeh.resources.INLINE)
        with open(output_fpath, "w") as f:
            f.write(html)


def _plot_selected_cols(
    dataset: hv.Dataset,
    model_info: models.ModelInfo,
    legend: tp.List[str],
    show_points: bool,
    backend: str,
) -> hv.NdOverlay:
    """
    Plot the  selected columns in a dataframe.
    """
    # Always plot the data
    plot = hv.Overlay(
        [
            hv.Curve(
                dataset,
                dataset.kdims[0],
                vdim.name,
                label=legend[dataset.vdims.index(vdim)] if legend else "",
            )
            for vdim in dataset.vdims
        ]
    )
    # Plot the points for each curve if configured to do so, OR if there aren't
    # that many. If you print them and there are a lot, you essentially get
    # really fat lines which doesn't look good.
    plot *= hv.Overlay(
        [
            hv.Points((dataset[dataset.kdims[0]], dataset[v]))
            for v in dataset.vdims
            if len(dataset[v]) <= 50 or show_points
        ]
    )

    if backend == "matplotlib":
        opts = {
            "linestyle": "--",
        }
    elif backend == "bokeh":
        opts = {"line_dash": [6, 3]}

    # Plot models if they have been computed
    if model_info.dataset:
        plot *= hv.Overlay(
            [
                hv.Curve(
                    model_info.dataset,
                    model_info.dataset.kdims[0],
                    vdim.name,
                    label=model_info.legend[model_info.dataset.vdims.index(vdim)],
                ).opts(**opts)
                for vdim in model_info.dataset.vdims
            ]
        )
        # Plot the points for each curve
        plot *= hv.Overlay(
            [
                hv.Points(
                    (
                        model_info.dataset[model_info.dataset.kdims[0]],
                        model_info.dataset[v],
                    )
                )
                for v in model_info.dataset.vdims
                if len(model_info.dataset[v]) <= 50 or show_points
            ]
        )

    return plot


def _plot_stats_stddev(dataset: hv.Dataset, stddev_df: pd.DataFrame) -> hv.NdOverlay:
    """Plot the stddev for all columns in the dataset."""
    stddevs = pd.DataFrame()
    for c in dataset.vdims:
        stddevs[f"{c}_stddev_l"] = dataset[c] - 2 * stddev_df[c.name].abs()
        stddevs[f"{c}_stddev_u"] = dataset[c] + 2 * stddev_df[c.name].abs()

    # To plot area between lines, you need to add the stddev columns to the
    # dataset
    dataset.data = pd.concat([dataset.dframe(), stddevs], axis=1)

    return hv.Overlay(
        [
            hv.Area(
                dataset, vdims=[f"{vdim.name}_stddev_l", f"{vdim.name}_stddev_u"]
            ).opts(
                alpha=0.5,
            )
            for vdim in dataset.vdims
        ]
    )


def _read_stats(
    setting: str, stats_root: pathlib.Path, input_stem: str, medium: str
) -> tp.Dict[str, pd.DataFrame]:
    dfs = {}  # type: tp.Dict[str, pd.DataFrame]
    settings = []

    if setting == "none":
        return dfs

    if setting == "all":
        settings = ["conf95", "bw"]
    else:
        settings = [setting]

    if setting in settings:
        exts = config.kStats[setting].exts

        for k in exts:
            ipath = stats_root / (input_stem + exts[k])
            if utils.path_exists(ipath):
                dfs[k] = storage.df_read(ipath, medium)
            else:
                _logger.warning("%s not found for '%s'", exts[k], input_stem)

    return dfs


# 2024/09/13 [JRH]: The union is for compatability with type checkers in
# python {3.8,3.11}.
def _read_models(
    model_root: tp.Optional[pathlib.Path], input_stem: str, medium: str
) -> models.ModelInfo:

    if model_root is None:
        return models.ModelInfo()

    modelf = model_root / (input_stem + config.kModelsExt["model"])
    legendf = model_root / (input_stem + config.kModelsExt["legend"])

    if not utils.path_exists(modelf):
        _logger.trace("Model file %s missing for graph", str(modelf))
        return models.ModelInfo()

    info = models.ModelInfo()
    df = storage.df_read(modelf, medium)
    cols = df.columns.tolist()

    info.dataset = hv.Dataset(data=df.reset_index(), kdims=["index"], vdims=cols)

    with utils.utf8open(legendf, "r") as f:
        info.legend = f.read().splitlines()

    _logger.trace(
        "Loaded model='%s',legend='%s'",  # type: ignore
        modelf.relative_to(model_root),
        legendf.relative_to(model_root),
    )

    return info


__all__ = ["generate"]
