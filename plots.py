import csv
import os
from datetime import datetime

import matplotlib.pyplot as plotlib
import numpy
import numpy as np


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


def plot_all(data_files: list, labels: list = None, plot_path: str = "./debug/hysplit_out/plots/"):
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
        plot_file = os.path.join(plot_path, f"{experiment}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.jpg")
        plot(all_data[0], numpy.mean(all_data[1:], axis=0), label, plot_file)
