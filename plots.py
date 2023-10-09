import csv
import os
from datetime import datetime
from math import comb
import matplotlib
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


def plot_qualities():
    all_data = np.asarray(get_rows('/Users/sriramrao/code/farsite/farsite_output/results.txt'))

    perimeter_res = [15, 30, 45, 60, 75, 90]
    colours = ['red', 'blue', 'cyan', 'orange', 'black', 'pink', 'green']

    print(len(all_data[0]))

    data = all_data
    distance_data = list()
    perimeter_data = list()
    # for i in range(0, len(perimeter_res)):
    # 	data = list()
    # 	for row in all_data:
    # 		if int(row[3]) != perimeter_res[i]:
    # 			continue
    # 		data.append(row)
    # 	data = np.asarray(data)
    # 	plotlib.plot(data[:, 2], data[:, 4], color=colours[i], alpha=0.65)

    # for row in all_data:
    #     # if int(row[2]) != 3:
    #     #     continue
    #     timestep_data.append([row[0], row[3]])
    #     distance_data.append([row[1], row[3]])
    #     perimeter_data.append([row[2], row[3]])
    data = np.asarray(data)
    plotlib.scatter(data[0:30, 0], data[0:30, 3], color='blue', alpha=0.65)
    plotlib.xlabel("timestep")
    plotlib.ylabel("quality")
    plotlib.show()

    plotlib.scatter(data[31:, 1], data[31:, 3], color='blue', alpha=0.65)
    plotlib.xlabel("distance resolution")
    plotlib.ylabel("quality")
    plotlib.show()

    plotlib.scatter(data[:, 2], data[:, 3], color='blue', alpha=0.65)
    plotlib.xlabel("perimeter resolution")
    plotlib.ylabel("quality")
    plotlib.show()


def plot_costs():
    all_data = np.asarray(get_rows('/Users/sriramrao/code/farsite/farsite_output/measures/perimeter_res_cost_float.txt'))

    perimeter_res = [15, 30, 45, 60, 75, 90]
    colours = ['red', 'blue', 'cyan', 'orange', 'black', 'pink', 'green']

    for i in range(0, len(perimeter_res)):
        res = perimeter_res[i]
        subset = all_data[(all_data[:, 3] == res)]
        cell_measures = list()
        for row in subset:
            cell_count = 4 * 5280 * 5280 / (row[2] * row[2])
            cost_per_cell = row[4] / cell_count
            size_projection = 60 * 30 / cost_per_cell * row[2] * row[2] / (5280 * 5280)
            cell_measures.append([cell_count, cost_per_cell, size_projection])
        cell_measures = np.asarray(cell_measures)
        # plotlib.scatter(subset[:, 2], subset[:, 4], color=colours[i], alpha=0.7)
        plotlib.scatter(subset[:, 2], cell_measures[:, 2], color=colours[i], alpha=0.7)

    # data = all_data
    # data = np.asarray(data)
    # plotlib.plot(data[:, 0], data[:, 4], color='blue', alpha=0.65)
    # plotlib.xlabel("timestep")
    # plotlib.ylabel("quality")
    # plotlib.show()


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


if __name__ == '__main__':
    plot_costs()
    plotlib.xlabel("distance resolution (feet)")
    plotlib.ylabel("projected input area size (sq. mi.)")
    plotlib.show()
