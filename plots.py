import csv
import os
import random
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plotlib
import numpy
import numpy as np
import pandas as pd
import seaborn
import seaborn as sns
from pandas import DataFrame

import util.files
from simulator import hysplit
from util import strings


def get_rows(full_path: str) -> list:
    rows = list()
    with open(full_path, 'r') as file:
        reader = csv.reader(file, delimiter="\t", quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            rows.append(row)
    return rows


def plot(x_data, y_data, label: tuple, save_file: str):
    plotlib.plot(x_data, y_data, color='blue', alpha=0.65)
    plotlib.xlabel(label[0])
    plotlib.ylabel(label[1])
    plotlib.savefig(save_file)
    plotlib.show()


def plot_line(x_data, y_data, colour: str):
    plotlib.plot(x_data, y_data, color=colour, alpha=0.65)


def set_labels(x_label, y_label):
    plotlib.xlabel(x_label)
    plotlib.ylabel(y_label)


def plot_all(data_files: list, labels: list = None, plot_path: str = "./debug/hysplit_out/plots/", ext: str = "pdf"):
    for index in range(len(data_files)):
        experiment, experiment_path, attempts = data_files[index][0], data_files[index][1], data_files[index][2]
        label = labels[index]
        all_data = list()
        for attempt in range(0, attempts):
            file = os.path.join(experiment_path, f"timings_{attempt}.txt")
            with open(file) as data_file:
                lines = csv.reader(data_file, delimiter="\t")
                data = [[float(value) for value in line] for line in lines]
            data = np.asarray(data)[1:]
            if len(all_data) == 0:
                all_data.append(data[:, 0])
            all_data.append(data[:, 1])
        all_data = np.asarray(all_data)
        plot_file = os.path.join(plot_path, f"{experiment}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.{ext}")
        plot(all_data[0], numpy.mean(all_data[1:], axis=0), label, plot_file)


def plot_qualities(config: dict, results_base_name: str = "measures",
                   base_path: str = "./debug/hysplit_out/", plots_base_path: str = "./debug/hysplit_out/plots",
                   ext: str = "pdf"):
    measures_path = (Path(base_path) / config["test_name"] / config["test_time"]
                     / f"{results_base_name}_{config['measure_time']}.csv").resolve()
    schema, lines = util.files.read(measures_path)
    lines = np.asarray(lines)
    param_name = config["measure_param"]
    lines = lines[lines[:, schema[param_name]].argsort()]
    param_values = [config["parse"](value) for value in lines[:, schema[param_name]]]
    data = dict()
    for constant_config in config["constants"]:
        instance_data = {param_name: list(), "mae": list(), "mse": list(), "times": list()}
        for i in range(0, len(param_values)):
            skip = False
            for param, value in constant_config.items():
                if param in schema and lines[i][schema[param]] != value:
                    skip = True
                    break
            if skip:
                continue
            value = param_values[i]
            instance_data[param_name].append(value)
            instance_data["mae"].append(Decimal(lines[i][schema["MAE"]]))
            instance_data["mse"].append(Decimal(lines[i][schema["MSE"]]))
            instance_data["times"].append(Decimal(lines[i][schema["DURATION_S"]]))
        data[constant_config["LABEL"]] = instance_data
    suffix = hysplit.get_date_suffix(datetime.now())
    param_clean = config["label"]
    plot_path = Path(plots_base_path).resolve() / param_clean.lower() / suffix
    plot_path.mkdir(parents=True, exist_ok=True)
    plot_measures = [(param_name, "mae"), (param_name, "mse"), (param_name, "times"), ("mae", "times"),
                     ("mse", "times")]
    for x_measure, y_measure in plot_measures:
        set_labels(x_measure.lower(), y_measure.lower())
        for constant in config["constants"]:
            plot_data = data[constant["LABEL"]]
            plot_line(plot_data[x_measure], plot_data[y_measure], constant["COLOR"])
        plotlib.savefig(str(plot_path / f"{x_measure.lower()}_{y_measure.lower()}_{suffix}.{ext}"))


bbox = (1.05, 1.00)


def plot_measures(durations_file: str, errors_file: str):
    base_path = Path("./debug/hysplit_out/plots/measures/" + strings.get_date_str()).resolve()
    base_path.mkdir(parents=True, exist_ok=True)
    sns.set_theme()
    durations = pd.read_csv(durations_file)
    durations["Spacing"] = durations.apply(
        lambda row: float(row["output_grids::spacing"].split(" ")[0]), axis=1).astype(float)
    durations["Sampling Rate"] = durations.apply(
        lambda row: hysplit.get_sampling_rate_mins(row["output_grids::sampling"]), axis=1).astype(int)
    durations = durations.drop(["mae", "mse", "mape", "attempt_id",
                                "output_grids::sampling", "output_grids::spacing"], axis=1)
    group_by_columns = durations.columns.tolist()
    group_by_columns.remove("duration_s")
    group_by_columns.remove("run_id")
    durations = durations.groupby(group_by_columns, as_index=False).agg({"duration_s": "mean", "run_id": "min"})

    errors = pd.read_csv(errors_file).drop_duplicates()
    measures = pd.merge(durations, errors, how="outer", on=["run_id"])
    group_by_columns.remove("total_run_time")
    measures = measures.drop(["total_run_time"], axis=1).groupby(group_by_columns, as_index=False).mean().reset_index()

    measures = measures.loc[(measures["Spacing"] != 0.001)]

    # , "rmse", "smape_ignore_missing"]]
    plot_details = [("Spacing", "Sampling Rate"), ("Sampling Rate", "Spacing")]
    metrics_needed = {("mae", "duration_s"): [("mae", "duration_s"),
                                ("mae_zscore", "duration_s_zscore")],
                      # ("smape_ignore_missing", "duration_s"): [("smape_ignore_missing", "duration_s"),
                      #                                          ("smape_ignore_missing_zscore", "duration_s_zscore")],
                      # ("rmse", "duration_s"): [("rmse", "duration_s"),
                      #                          ("rmse_zscore", "duration_s_zscore")]
                      }
    for variable, group in plot_details:
        for base_metrics, columns in metrics_needed.items():
            for column in columns:
                calculate_measure(measures, variable, group, base_metrics[0], base_metrics[1],
                                  column[0], column[1], base_path=base_path)
        for metric in {item for sublist in metrics_needed.keys() for item in sublist}:
            calculate_measure(measures, variable, group, variable, metric,
                              variable, metric, x_avg=False, base_path=base_path)
            calculate_measure(measures, variable, group, variable, metric,
                              variable, metric + "_zscore", x_avg=False, base_path=base_path)

    # metrics_needed = ["duration_s", "mae", "duration_s_zscore", "mae_zscore"]
    # for variable, group in plot_details:
    #     for metric in metrics_needed:
    #         measures = calculate_z_scores(measures, "mae", group)
    #         measures = calculate_z_scores(measures, "duration_s", group)
    #         sns.lineplot(x=variable, y=metric, hue=group, data=measures.sort_values(variable),
    #                      palette=seaborn.color_palette("colorblind")).set_title(variable)
    #         plotlib.legend(loc="upper right", bbox_to_anchor=bbox, title=group)
    #         save_path = base_path / f"{variable}_{metric}.pdf"
    #         plotlib.savefig(str(save_path))
    #         plotlib.show()


def calculate_measure(dataframe: DataFrame, variable: str, group: str, x_metric: str, y_metric: str,
                      x_column: str = None, y_column: str = None,
                      x_avg: bool = True, y_avg: bool = True, base_path: Path = Path()):
    subset = [variable, group]
    if x_metric not in subset: subset.append(x_metric)
    if y_metric not in subset: subset.append(y_metric)
    measures = dataframe[subset].drop_duplicates()
    measures = calculate_z_scores(measures, x_metric, group)
    measures = calculate_z_scores(measures, y_metric, group)
    y_zscore = f"{y_metric}_zscore"
    x_zscore = f"{x_metric}_zscore"
    measures[group] = measures[group].apply(lambda x: Decimal(x))
    # average_cols = [variable]
    # if x_avg: average_cols.append(x_metric)
    # if y_avg: average_cols.append(y_metric)
    # averages = measures[average_cols]
    # averages = averages.drop_duplicates()
    # averages = averages.groupby(variable, as_index=False).agg("mean")
    # averages[group] = -1
    # rename_columns = {}
    # if x_avg:
    #     rename_columns[f"{x_metric}_mean"] = x_metric
    # if y_avg:
    #     rename_columns[f"{y_metric}_mean"] = y_metric
    # averages = averages.rename(columns=rename_columns)
    # measures = pd.concat([measures, averages])

    temp_palette = [color + (0.4,) for color in
                                    sns.color_palette(['grey'], len(measures[group].unique()))]
    x_measure = x_zscore if not x_column else x_column
    y_measure = y_zscore if not y_column else y_column

    # line_styles = {value: ((4, 2) if int(value) != -1 else (None, None)) for value in measures[group].values}
    ax = sns.lineplot(x=x_measure, y=y_measure, hue=group, data=measures, estimator="mean", errorbar='sd', palette=temp_palette)  # .sort_values(x_measure),
                      # style=group)  #, dashes=line_styles, )
    labels = list()
    handles = ax.legend().legend_handles
    for handle in ax.legend().legend_handles:
        label = "%.3g" % Decimal(handle.get_label())
        labels.append(label if int(Decimal(label)) != -1 else "Average")
    ax.set_title(variable)
    ax.legend(handles, labels, loc="upper right", bbox_to_anchor=bbox, title=group)
    save_path = base_path / f"{variable}_{x_measure}_{y_measure}.pdf"
    plotlib.savefig(str(save_path))
    plotlib.show()
    measures = measures.drop([y_metric + "_zscore", x_metric + "_zscore"], axis=1)
    return measures.loc[measures[group] != -1]


def get_color():
    return random.choice(seaborn.color_palette("husl"))


def get_decimal(value) -> Decimal:
    return Decimal(value)


def calculate_z_scores(dataframe: DataFrame, measure_name: str, group_by: str) -> DataFrame:
    measures = dataframe.groupby(group_by, as_index=False).agg({measure_name: ["mean", "std"]})
    measures.columns = [level1 + ('_' + level2 if level2 else "") for level1, level2 in measures.columns]
    dataframe = dataframe.merge(measures, on=group_by)
    dataframe[f"{measure_name}_zscore"] = ((dataframe[measure_name] - dataframe[f"{measure_name}_mean"])
                                           / dataframe[f"{measure_name}_std"])

    dataframe = dataframe.drop([measure_name + "_mean", measure_name + "_std"], axis=1)
    return dataframe


def scale_measure(dataframe: DataFrame, measure_name: str):
    min_measure, diff_measure = f"min_{measure_name}", f"{measure_name}_diff"
    max_measure = f"max_{measure_name}"
    columns = list(dataframe.columns)
    columns.remove(measure_name)
    measures = dataframe.groupby(columns).agg({measure_name: ["mean", "std"]})
    dataframe = dataframe.merge(measures, left_on=columns, right_index=True)
    # dataframe[diff_measure] = dataframe[measure_name] - dataframe[min_measure]
    # dataframe["max_diff"] = dataframe.groupby(columns, as_index=False)[diff_measure].transform("max")
    # dataframe[f"scaled_{measure_name}"] = dataframe[diff_measure] / dataframe["max_diff"]
    return dataframe
