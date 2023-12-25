import copy
import random
from decimal import Decimal
from pathlib import Path

import math
import matplotlib.pyplot as plotlib
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas import DataFrame
from scipy.stats.mstats import gmean

from simulator import hysplit
from util import strings


class Label:
    average_label = "Average"
    variable = "variable"
    constant = "constant"


class MeasureType:
    log = "log"
    zscore = "zscore"
    relative = "relative"
    percent = "percent"
    log_scale = "log_scale"
    square = "square"
    weighted = "weighted"


class Dimension:
    def __init__(self, name: str, axis_label: str, title_label: str):
        self.name = name
        self.axis_label = axis_label
        self.title_label = title_label


class Metric:
    error = "error"

    def __init__(self, name: str, axis_label: str, title_label: str = None, measure: str = "", metric_type: str = ""):
        self.name = name
        self.axis_label = axis_label
        self.title_label = title_label if title_label else axis_label
        self.measure = measure
        self.metric_type = metric_type

    def replace_placeholders(self, old: str, replacement: Dimension):
        self.name = self.name.replace(old, replacement.name)
        self.axis_label = self.axis_label.replace(old, replacement.axis_label)
        self.title_label = self.title_label.replace(old, replacement.title_label)

    def get_measure_name(self) -> str:
        return self.name + (f"_{self.measure}" if self.measure and MeasureType.log != self.measure else "")


class PlotConfig:
    def __init__(self, x: Metric, y: Metric, title: str = None, show_trend: bool = True):
        self.x = x
        self.y = y
        self.show_trend = show_trend
        self.constant = None
        self.variable = None
        self.title = title if title else self.set_title()

    def replace_placeholders(self, old: str, replacement: Dimension):
        self.x.replace_placeholders(old, replacement)
        self.y.replace_placeholders(old, replacement)
        self.set_title()

    def set_title(self):
        self.title = self.x.title_label + " vs " + self.y.title_label

    def set_info(self, info: dict):
        self.constant = info[Label.constant]
        self.replace_placeholders(Label.constant, self.constant)
        self.variable = info[Label.variable]
        self.replace_placeholders(Label.variable, self.variable)


variable_labels = {
    "spacing": Dimension("spacing", "Spacing (degrees)", "Node Spacing"),
    "sampling_duration": Dimension("sampling_duration", "Interval (minutes)", "Sampling Interval")
}


def get_plot_config():
    plot_info = [
        {"variable": variable_labels["spacing"], "constant": variable_labels["sampling_duration"]},
        {"variable": variable_labels["sampling_duration"], "constant": variable_labels["spacing"]}
    ]

    x_variables = [
        Metric(Label.variable, Label.variable, Label.variable),
        Metric("mse", "MSE %", "Error (MSE) %", MeasureType.percent,
               metric_type=Metric.error),
    ]

    y_variables = [
        # Metric("duration_s", "Execution Time (seconds)", "Cost (seconds)"),
        Metric("duration_s", "Execution Time %", "Cost", MeasureType.percent),
        Metric("mse", "MSE %", "Error (MSE) %", MeasureType.percent, metric_type=Metric.error)
    ]

    plot_description = list()
    for x in x_variables:
        for y in y_variables:
            if x.name == y.name or x.metric_type == y.metric_type == Metric.error:
                continue
            plot_description.append(PlotConfig(x, y))

    # remove_columns = {"total_run_time"}
    return plot_info, plot_description


def plot_measures(durations_file: str, errors_file: str, save: bool = False):
    base_path = Path("./debug/hysplit_out/plots/measures/" + strings.get_date_str()).resolve()
    plot_info, plot_description = get_plot_config()

    durations = get_durations(durations_file)
    errors = get_errors(errors_file)
    measures = pd.merge(durations, errors, how="outer", on=["run_id"])

    for info in plot_info:
        measures[info[Label.constant].name] = measures[info[Label.constant].name].apply(lambda x: Decimal(x))
        figure, axes = get_layout(1, len(plot_description))
        for i, description in enumerate(plot_description):
            config = copy.deepcopy(description)
            config.set_info(info)
            plot_data = remove_unneeded_points(measures, config)
            plot_data = get_plot_measures(plot_data, config)
            plot_dataset(plot_data, config, axes[0][i])
        complete_plot(figure, axes, info, save, base_path)


def get_durations(measures_path: str):
    path = Path(measures_path)
    durations = pd.read_csv(path / "runtime_measurements_0.csv")
    durations.columns = durations.columns.str.lower()
    for measure_file in Path(measures_path).resolve().glob("runtime_measurements*"):
        if "runtime_measurements_0" == measure_file.stem:
            continue
        measures = pd.read_csv(measure_file)
        durations = pd.concat([durations, measures])
    durations["spacing"] = durations.apply(
        lambda row: float(row["output_grids::spacing"].split(" ")[0]), axis=1).astype(float)
    durations["sampling_duration"] = durations.apply(
        lambda row: hysplit.get_sampling_rate_mins(row["output_grids::sampling"]), axis=1).astype(int)

    durations = durations.drop(["mae", "mse", "mape", "attempt_id",
                                "output_grids::sampling", "output_grids::spacing"], axis=1, errors='ignore')
    group_by_columns = durations.columns.tolist()
    group_by_columns.remove("duration_s")
    return durations.groupby(group_by_columns, as_index=False).agg({"duration_s": "mean"})


def get_errors(file: str):
    errors = pd.read_csv(file).drop_duplicates()
    errors = errors[["attempt_id", "run_id", "mae", "mse", "mape"]]
    errors["rmse"] = errors["mse"] ** 0.5
    return errors


def get_plot_measures(dataframe: DataFrame, description: PlotConfig) -> DataFrame:
    columns_needed = {description.variable.name, description.constant.name, description.x.name, description.y.name}
    plot_data = (dataframe[list(columns_needed)]
                 .groupby([description.variable.name, description.constant.name], as_index=False)
                 .mean())

    if description.show_trend:
        plot_data = add_mean(plot_data, description)
    if description.x.measure:
        plot_data = add_measure(plot_data, description.constant.name, description.x.name, description.x.measure)
    if description.y.measure:
        plot_data = add_measure(plot_data, description.constant.name, description.y.name, description.y.measure)
    return plot_data.drop_duplicates().dropna()


def add_mean(dataframe: DataFrame, config: PlotConfig, average_label=Label.average_label) -> DataFrame:
    x_measure, y_measure = config.x.name, config.y.name
    columns = {config.variable.name, x_measure, y_measure}
    average_methods = {
        x_measure: "mean" if MeasureType.log_scale != config.x.measure else gmean,
        y_measure: "mean" if MeasureType.log_scale != config.y.measure else gmean
    }
    averages = dataframe[list(columns)].groupby(config.variable.name, as_index=False).agg(average_methods)
    averages[config.constant.name] = average_label
    return pd.concat([dataframe, averages])


measure_calculators = {
    MeasureType.zscore: {"aggregates": ["mean", "std"],
                         "compute_from_row": lambda row, y: (row[y] - row[f"{y}_mean"]) / row[f"{y}_std"]},
    MeasureType.relative: {"aggregates": ["max"],
                           "compute_from_row": lambda row, metric: 100 * Decimal(row[metric] / row[f"{metric}_max"])},
    MeasureType.log: None,
    MeasureType.percent: {"aggregates": ["min", "max"], "compute_from_row":
        lambda row, y: (row[y] - row[f"{y}_min"]) * 100 / (row[f"{y}_max"] - row[f"{y}_min"])},
    MeasureType.log_scale: {"compute_from_row": lambda row, y: math.log(100 * row[y], 2)},
    MeasureType.square: {"compute_from_row": lambda row, y: row[y] ** 2}
}


def add_measure(dataframe: DataFrame, dimension: str, metric: str, measure_type: str) -> DataFrame:
    if measure_type not in measure_calculators or not measure_calculators[measure_type]:
        return dataframe
    calculator = measure_calculators[measure_type]
    measures = dataframe
    if "aggregates" in calculator and calculator["aggregates"]:
        measures = measures.groupby(dimension, as_index=False).agg({metric: calculator["aggregates"]})
        measures.columns = [level1 + ('_' + level2 if level2 else "") for level1, level2 in measures.columns]
        dataframe = dataframe.merge(measures, on=dimension)
    dataframe[f"{metric}_{measure_type}"] = dataframe.apply(lambda row: calculator["compute_from_row"](row, metric),
                                                            axis=1)
    for agg in calculator.get("aggregates", list()):
        dataframe = dataframe.drop([f"{metric}_{agg}"], axis=1)
    return dataframe


def remove_unneeded_points(dataframe: DataFrame, description: PlotConfig) -> DataFrame:
    dataframe = dataframe.query("spacing > 0.01 and sampling_duration > 1")
    # if description.x.name == "spacing" and description.y.metric_type == Metric.error:
    #     dataframe = dataframe.loc[(dataframe["spacing"] * 100) % 2 == 1]
    dataframe = dataframe.query("sampling_duration <= 120")
    # dataframe = dataframe.query("")
    # check if hysplit samples at an internal fixed rate
    return dataframe


def get_layout(rows: int = 1, columns: int = 1) -> (Figure, [[Axes]]):
    sns.set(style="whitegrid", font_scale=3, font="Times New Roman")
    return plotlib.subplots(rows, columns, figsize=(8 * columns, 8), squeeze=False)


def complete_plot(figure: Figure, axes: [[Axes]], info: {str: Dimension}, save: bool, base_path: Path):
    labels = list()
    handles, labels_default = axes[0][0].get_legend_handles_labels()
    for handle in axes[0][0].legend().legend_handles:
        label = "%.3g" % Decimal(handle.get_label()) if handle.get_label() != "Average" else "Average"
        labels.append(label)
    for row in axes:
        for axis in row:
            axis.get_legend().set_visible(False)
    columns = len(handles)
    legend = figure.legend(handles, labels, title=info["constant"].title_label, framealpha=1.0, loc="center",
                           title_fontproperties={"weight": "bold", "size": 32},
                           prop={"weight": "bold", "size": 28},
                           facecolor="white", edgecolor="grey", bbox_to_anchor=(0.5, 1.02), ncols=columns,
                           borderpad=0.1)
    legend.get_frame().set_linewidth(2.5)
    # figure.suptitle(f"{info['variable'].title_label}: Error and Cost", y=0.95, fontsize=30, fontweight="bold")
    figure.tight_layout()

    if save:
        base_path.mkdir(parents=True, exist_ok=True)
        save_path = base_path / f"{info['variable'].name}_per_{info['constant'].name}.pdf"
        plotlib.savefig(str(save_path), dpi=500, bbox_inches="tight", bbox_extra_artists=(legend,))
    figure.subplots_adjust(top=0.9)
    plotlib.show(dpi=500, bbox_inches="tight", bbox_extra_artists=(legend,))


def plot_dataset(dataframe: DataFrame, description: PlotConfig, axis: Axes):
    hue, unique_values = None, None
    if description.constant:
        dataframe = dataframe.sort_values([description.constant.name, description.x.name], ascending=[False, True])
        hue = description.constant.name
        unique_values = dataframe[hue].unique()
    averages = dataframe.query(f"{description.constant.name} == '{Label.average_label}'")
    dataframe = dataframe.query(f"{description.constant.name} != '{Label.average_label}'")
    palette = sns.color_palette("colorblind") if unique_values is None \
        else {v: get_sub_line_color() for v in unique_values}
    palette.update({Label.average_label: get_main_line_color()})

    sns.lineplot(x=description.x.get_measure_name(), y=description.y.get_measure_name(), data=averages,
                 # label="Average",
                 style=hue, markers="o", markersize=20, color=get_main_line_color(), errorbar=None, estimator="mean",
                 lw=7,
                 ax=axis)
    sns.lineplot(x=description.x.get_measure_name(), y=description.y.get_measure_name(), data=dataframe,
                 hue=hue, style=hue, markers=True, markersize=10, palette=palette, ax=axis)
    if MeasureType.log == description.x.measure:
        axis.set(xscale="log")
    if MeasureType.log == description.y.measure:
        axis.set(yscale="log")

    axis.set_title(description.title, fontsize=40, fontweight="bold")
    axis.set_xlabel(description.x.axis_label, fontsize=37, fontweight="bold")
    axis.tick_params(axis="both", labelsize=36)
    axis.set_ylabel(description.y.axis_label, fontsize=37, fontweight="bold")
    return axis


def get_color():
    # yellow: rgba(255,174,52,255), #ffae34, blue: rgba(99,136,180,255), #6388b4
    return random.choice(sns.color_palette("husl"))


def get_main_line_color():
    return random.choice([(255 / 255, 174 / 255, 52 / 255, 255 / 255)])  # , "#6388b4"])


def get_sub_line_color():
    return 99 / 255, 136 / 255, 180 / 255, 0.6
