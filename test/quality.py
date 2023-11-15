# need a way to distinguish between timestamp outputs -- assume chronological
# how do we quantify quality gained by finer granularity?
import itertools
import os.path
from _decimal import Decimal
from datetime import datetime

from model.shape import Point, Box
from simulator.hysplit import Hysplit
from test.error_measures import get_error, aggregate
from test.hysplit_test import get_output_files, get_test_prefix, coarse_value_for_sampling_test


class HysplitResult:
    def __init__(self, path: str, parameters: dict = None):
        self.parameters = {"%spacing%": "0.001 0.001",
                           "%sampling%": "01 00",
                           "%grid_center%": "35.727513, -118.786136",
                           "%span%": "180.0 360.0"}
        if parameters is not None:
            for key in parameters.keys():
                self.parameters[key] = parameters[key]
        self.path = path
        self.results = None

    def set_parameter(self, name: str, value: str) -> None:
        self.parameters[name] = value

    def fetch_results(self) -> [dict]:
        if self.results is not None:
            return self.results
        hysplit = Hysplit()
        hysplit.set_parameter("%data_output%", self.path)
        self.results = hysplit.get_results()
        return self.results


def measure_quality(param_name: str, test_name: str, test_time: str, constants: dict = None,
                    base_path: str = "./debug/hysplit_out", attempts: int = 1):
    if not constants:
        constants = dict()
    test_date = datetime.strptime(test_time, "%Y-%m-%d %H:%M")
    base_config = HysplitResult(f"{base_path}/{test_name}/2023-09-14_04-44/0/dump_5.txt",
                                {"%sampling%": "00 00 05"})
    outputs = get_output_files(test_name, test_date, base_path, attempts)
    for attempt in range(0, len(outputs)):
        print(f"Attempt: {attempt}\n")
        output_set = outputs[attempt]
        measures_lines = ['param\ttime\tmae\tmse']
        for param, time, file in output_set:
            print(f"Starting: {param}\n")
            param_value = param
            if "%spacing%" == param_name:
                param_value = f"{param} {param}"
            elif "%sampling%" == param_name:
                param_value = f"00 {int(param) / 60} {int(param) % 60}"
            test_config = HysplitResult(file, {param_name: param_value})
            for key in constants.keys():
                test_config.set_parameter(key, constants[key])

            errors = compare_quality(test_config, base_config, coarse_value_for_sampling_test)
            mae = round(errors["total_mae"], 5)
            mse = round(errors["total_mse"], 5)
            measures_lines.append(f"{param}\t{time}\t{mae}\t{mse}")
        measures_path = os.path.join(get_test_prefix(base_path, test_name, test_date), f"measures_{attempt}.tsv")
        with open(measures_path, 'w') as measures_file:
            measures_file.write("\n".join(measures_lines))


def compare_quality(test_result: HysplitResult, ground_truth_result: HysplitResult,
                    compute_coarse_value=lambda v, rows: v, error_types: [str] = None):
    measure_types = error_types if error_types else ["mae", "mse"]
    test_result.fetch_results()
    ground_truth_result.fetch_results()
    return compute_errors(test_result, ground_truth_result, compute_coarse_value, measure_types)


def compute_errors(dataset1: HysplitResult, dataset2: HysplitResult,
                   compute_coarse_value, error_types: [str]) -> dict:
    dataset_fine, dataset_coarse = validate_datasets(dataset1, dataset2)
    errors = dict()
    for row in dataset_coarse.results:
        relevant_fine_data = [Decimal(row["concentration"])
                              for row in get_matching_data(row, dataset_coarse, dataset_fine)]
        if len(relevant_fine_data) == 0:
            relevant_fine_data.append(Decimal(0))
        for error_type in error_types:
            if error_type not in errors:
                errors[error_type] = list()
            errors[error_type].append(
                get_error(Decimal(row["concentration"]), relevant_fine_data, compute_coarse_value, error_type))
    for measure_type in error_types:
        errors[f"total_{measure_type}"] = aggregate(errors[measure_type], measure_type)
    return errors


def validate_datasets(dataset1, dataset2) -> tuple:
    # can also add span and center validation if needed
    spacing1 = get_width(dataset1.parameters["%spacing%"])
    spacing2 = get_width(dataset2.parameters["%spacing%"])
    dataset_fine, dataset_coarse = dataset1, dataset2
    if spacing1 > spacing2:
        dataset_fine, dataset_coarse = dataset2, dataset1
        spacing1, spacing2 = spacing2, spacing1
    if spacing2 / spacing1 != int(spacing2 / spacing1):
        raise Exception("Cannot compare: the smaller spacing does not divide the larger spacing")
    return dataset_fine, dataset_coarse


def get_matching_data(row: dict, dataset_coarse: HysplitResult, dataset_fine: HysplitResult) -> [dict]:
    fine_spacing = get_width(dataset_fine.parameters["%spacing%"])
    coarse_spacing = get_width(dataset_coarse.parameters["%spacing%"])
    grid_bounds = get_cell_bounds(row["latitude"], row["longitude"], coarse_spacing)
    relevant_data = list()
    for fine_row in dataset_fine.fetch_results():
        row_bounds = get_cell_bounds(fine_row["latitude"], fine_row["longitude"], fine_spacing)
        if row["timestamp"] == fine_row["timestamp"] and grid_bounds["box"].overlaps(row_bounds["box"]):
            relevant_data.append(fine_row)
    return relevant_data


def get_width(width: str) -> Decimal:
    return Decimal(round(Decimal(width.split(" ")[0]), 4))


def get_cell_bounds(latitude: str, longitude: str, width: Decimal) -> dict:
    grid_center = Point(Decimal(latitude), Decimal(longitude))
    lower = Point(grid_center.latitude - width / 2, grid_center.longitude - width / 2)
    upper = Point(grid_center.latitude + width / 2, grid_center.longitude + width / 2)
    grid_bounds = {"center": grid_center,
                   "box": Box(lower, upper),
                   "width": width}
    return grid_bounds


def get_decimal_list(start, end, step) -> list:
    value = start
    values = list()
    while value <= end:
        values.append(value)
        value += step
    return values
