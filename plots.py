import csv
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plotlib
import numpy
import numpy as np

import util.util
from simulator import hysplit


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


def plot_all(data_files: list, labels: list = None, plot_path: str = "./debug/hysplit_out/plots/", ext: str = "jpg"):
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
                   ext: str = "jpg"):
    measures_path = (Path(base_path) / config["test_name"] / config["test_time"]
                     / f"{results_base_name}_{config['measure_time']}.csv").resolve()
    schema, lines = util.util.FileUtil.read(measures_path)
    lines = np.asarray(lines)
    param_name = config["measure_param"]
    lines = lines[lines[:, schema[param_name]].argsort()]
    param_values = [config["parse"](value) for value in lines[:, schema[param_name]]]
    data = {param_name: list(), "mae": list(), "mse": list(), "times": list()}
    for i in range(0, len(param_values)):
        skip = False
        for param, value in config["constants"]:
            if lines[i][schema[param]] != value:
                skip = True
                break
        if skip: continue
        value = param_values[i]
        data[param_name].append(value)
        data["mae"].append(Decimal(lines[i][schema["MAE"]]))
        data["mse"].append(Decimal(lines[i][schema["MSE"]]))
        data["times"].append(Decimal(lines[i][schema["DURATION_S"]]))
    suffix = hysplit.get_date_suffix(datetime.now())
    param_clean = config["label"]
    plot_path = Path(plots_base_path).resolve() / param_clean.lower()
    plot_path.mkdir(parents=True, exist_ok=True)
    plot(data[param_name], data["mae"], (param_clean, "MAE"), str(plot_path / f"abs_error_{suffix}.{ext}"))
    plot(data[param_name], data["mse"], (param_clean, "MSE"), str(plot_path / f"sq_error_{suffix}.{ext}"))
    plot(data[param_name], data["times"], (param_clean, "Time"), str(plot_path / f"times_{suffix}.{ext}"))
    plot(data["mae"], data["times"], ("MAE", "Time"), str(plot_path / f"mae_time_{suffix}.{ext}"))
    plot(data["mse"], data["times"], ("MSE", "Time"), str(plot_path / f"mse_time_{suffix}.{ext}"))
