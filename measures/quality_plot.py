import copy
import random
from decimal import Decimal
from pathlib import Path

import math
import matplotlib.pyplot as plotlib
import pandas as pd
import seaborn
import seaborn as sns
from pandas import DataFrame
from scipy.stats.mstats import gmean

from simulator import hysplit
from util import strings


class Label:
    average_label = -1
    variable = "variable"
    constant = "constant"


class MeasureType:
    log = "log"
    zscore = "zscore"
    relative = "relative"
    percent = "percent"
    log_scale = "log_scale"


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
        prefix = f"{self.variable.title_label}: " if self.variable and self.variable.name != self.x.name else ""
        self.title = prefix + self.x.title_label + " v " + self.y.title_label

    def set_info(self, info: dict):
        self.constant = info[Label.constant]
        self.replace_placeholders(Label.constant, self.constant)
        self.variable = info[Label.variable]
        self.replace_placeholders(Label.variable, self.variable)

    def get_save_path(self, base_path: Path) -> Path:
        return base_path / f"{self.variable.name}_{self.x.get_measure_name()}_{self.y.get_measure_name()}.pdf"


variable_labels = {
    "spacing": Dimension("spacing", "Spacing (degrees)", "Spacing"),
    "sampling_duration": Dimension("sampling_duration", "Sampling Duration (minutes)", "Sampling Duration")
}


def get_plot_config():
    plot_info = [
        {"variable": variable_labels["spacing"], "constant": variable_labels["sampling_duration"]},
        {"variable": variable_labels["sampling_duration"], "constant": variable_labels["spacing"]}
    ]

    x_variables = [
        Metric(Label.variable, Label.variable, Label.variable),
        # Metric("rmse", "Root Mean Square Error", "Error (RMSE)", metric_type=Metric.error),
        # Metric("rmse", "Relative Root Mean Square Error", "Relative Error (RMSE)",
        #        MeasureType.relative, Metric.error),
        # Metric("rmse", "Root Mean Square Error", "Error (RMSE)", LOG),
        # Metric("rmse", "log(RMSE)", "Log of Error (RMSE)", MeasureType.log_scale),
        # Metric("smape_ignore_missing", "MAPE", "Error (MAPE)", metric_type=Metric.error),
        # Metric("smape_ignore_missing", "Relative MAPE %", "Relative Error (MAPE) %", MeasureType.percent, Metric.error),
        # Metric("smape_ignore_missing", "MAPE", "Error (MAPE)", MeasureType.log, Metric.error),
        # Metric("smape_ignore_missing", "MAPE Z-Score", "Error Z-Score (MAPE)", MeasureType.zscore, Metric.error),
        # Metric("smape", "Log MAPE", "Log Error (MAPE)", MeasureType.log_scale, Metric.error),
        # Metric("rmse", "Root Mean Square Error Z-Score", "Error Z-Score (RMSE)", ZSCORE),
    ]

    y_variables = [
        Metric("duration_s", "Execution Time (seconds)", "Cost"),
        # Metric("duration_s", "Relative Execution Time (%)", "Relative Cost %", MeasureType.percent),
        # Metric("duration_s", "Execution Time Z-Score", "Cost Z-Score", MeasureType.zscore),
        # Metric("duration_s", "Execution Time", "Cost", MeasureType.log),
        # Metric("rmse", "Root Mean Square Error", "Error (RMSE)", metric_type=Metric.error),
        # Metric("smape_ignore_missing", "MAPE", "Error (MAPE)", metric_type=Metric.error),
        # Metric("smape_ignore_missing", "Relative MAPE", "Relative Error (MAPE)", MeasureType.relative, Metric.error),
        # Metric("smape_ignore_missing", "MAPE Z-Score", "Error Z-Score (MAPE)", MeasureType.zscore, Metric.error),
        # Metric("smape_ignore_missing", "Log MAPE", "Log Error (MAPE)", MeasureType.log_scale, Metric.error),
        # Metric("rmse", "Relative Root Mean Square Error", "Relative Error (RMSE)", MeasureType.relative, Metric.error),
        # Metric("rmse", "Relative Root Mean Square Error", "Relative Error (RMSE)", MeasureType.relative, Metric.error),
        # Metric("rmse", "Root Mean Square Error", "Error (RMSE)", LOG),
        # Metric("rmse", "log(RMSE)", "Log Error (RMSE)", MeasureType.log_scale),
        # Metric("rmse", "Root Mean Square Error Z-Score", "Error Z-Score (RMSE)", ZSCORE),
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
        for description in plot_description:
            config = copy.deepcopy(description)
            config.set_info(info)
            plot_data = get_plot_measures(measures, config)
            plot_dataset(plot_data, config, save, base_path)


def get_durations(file: str):
    durations = pd.read_csv(file)
    durations["spacing"] = durations.apply(
        lambda row: float(row["output_grids::spacing"].split(" ")[0]), axis=1).astype(float)
    durations["sampling_duration"] = durations.apply(
        lambda row: hysplit.get_sampling_rate_mins(row["output_grids::sampling"]), axis=1).astype(int)

    # durations = durations.loc[(durations["spacing"] != 0.001) & (durations["spacing"] != 0.05)]  # generalise
    # durations = durations.loc[(durations["spacing"] <= 0.02) & (0.001 < durations["spacing"])]
    durations = durations.loc[(durations["total_run_time"] == 240)]
    # durations = durations.loc[(durations["sampling_duration"] > 10)]  # generalise

    durations = durations.drop(["mae", "mse", "mape", "attempt_id",
                                "output_grids::sampling", "output_grids::spacing"], axis=1)
    group_by_columns = durations.columns.tolist()
    group_by_columns.remove("duration_s")
    group_by_columns.remove("run_id")
    return durations.groupby(group_by_columns, as_index=False).agg({"duration_s": "mean", "run_id": "min"})


def get_errors(file: str):
    return pd.read_csv(file).drop_duplicates()


def get_plot_measures(dataframe: DataFrame, description: PlotConfig) -> DataFrame:
    columns_needed = {description.variable.name, description.constant.name, description.x.name, description.y.name}
    plot_data = (dataframe[list(columns_needed)]
                 .groupby([description.variable.name, description.constant.name], as_index=False)
                 .mean())

    if description.x.measure:
        plot_data = add_measure(plot_data, description.constant.name, description.x.name, description.x.measure)
    if description.y.measure:
        plot_data = add_measure(plot_data, description.constant.name, description.y.name, description.y.measure)
    if description.show_trend:
        plot_data = add_mean(plot_data, description)
    return plot_data.drop_duplicates().dropna()


def add_mean(dataframe: DataFrame, config: PlotConfig, average_label=Label.average_label) -> DataFrame:
    x_measure, y_measure = config.x.get_measure_name(), config.y.get_measure_name()
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
        lambda row, y: (row[y] - row[f"{y}_min"]) / (row[f"{y}_max"] - row[f"{y}_min"])
                          },
    MeasureType.log_scale: {"compute_from_row": lambda row, y: math.log(100 * row[y], 2)}
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


def plot_dataset(dataframe: DataFrame, description: PlotConfig, save: bool = True,
                 base_path: Path = Path("./debug/hysplit_out/plots/")):
    palette = sns.color_palette("colorblind")
    hue = description.constant.name if description.constant else None
    # if description.show_trend and description.constant:
    #     palette = ([get_color()] +
    #                [color + (0.4,) for color in
    #                 sns.color_palette(['grey'], len(dataframe[description.constant.name].unique()) - 1)])

    # dataframe = dataframe.loc[dataframe[description.y.get_measure_name()] < 1]
    # dataframe = dataframe.loc[dataframe[description.x.get_measure_name()] < 1]

    sns.set(font_scale=1.2, rc={'figure.figsize': (11, 8)})
    ax = sns.lineplot(x=description.x.get_measure_name(), y=description.y.get_measure_name(), hue=hue,
                      data=dataframe,
                      palette=palette, errorbar=None)
    if MeasureType.log == description.x.measure:
        ax.set(xscale='log')
    if MeasureType.log == description.y.measure:
        ax.set(yscale='log')
    labels = list()
    handles = ax.legend().legend_handles
    for handle in ax.legend().legend_handles:
        label = "%.3g" % Decimal(handle.get_label())
        labels.append(label if int(Decimal(label)) != Label.average_label else "Average")
    ax.set_title(description.title)
    ax.set(xlabel=description.x.axis_label, ylabel=description.y.axis_label)
    ax.legend(handles, labels, loc="upper center", title=description.constant.axis_label,
              bbox_to_anchor=(1.05, 1.0), framealpha=0.4)

    if save:
        base_path.mkdir(parents=True, exist_ok=True)
        plotlib.savefig(str(description.get_save_path(base_path)), dpi=500)
    plotlib.show()


def get_color():
    return random.choice(seaborn.color_palette("husl"))
