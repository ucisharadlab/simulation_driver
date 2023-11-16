from _decimal import Decimal
from datetime import datetime, timedelta
from pathlib import Path

from model.shape import Point, Box
from simulator import hysplit
from simulator.hysplit import Hysplit
from test_helpers import hysplit_test
from measures.error_measures import get_error, aggregate


spacing_param_key = "%output_grids%::%spacing%"
sampling_param_key = "%output_grids%::%sampling%"


class HysplitResult:
    def __init__(self, path: Path, parameters: dict = None):
        self.parameters = dict()
        if parameters is not None:
            self.parameters.update(parameters)
        self.path = path
        self.results = None

    def set_parameter(self, name: str, value: str) -> None:
        self.parameters[name] = value

    def fetch_results(self) -> [dict]:
        if self.results is not None:
            return self.results
        simulator = Hysplit(self.parameters)
        simulator.set_parameter("%data_output%", str(self.path))
        self.results = simulator.get_results()
        return self.results


def measure_quality(test_details: dict, base_details: dict, base_path: str = "./debug/hysplit_out"):
    base_config = get_result_config(base_path, base_details, base_details["run_id"])
    measures_path = hysplit_test.get_quality_path(base_path, test_details)

    with measures_path.open('a+') as file:
        for line in hysplit_test.get_measures(test_details['name'], test_details["date"], base_path):
            print(f"Starting: {line['run_id']}\n")

            test_config = get_result_config(base_path, test_details, line['run_id'])
            test_params = list()
            for key, value in line.items():
                if key in hysplit_test.get_measures_meta_attributes():
                    continue
                test_params.append(key)
                param_name, param_value = hysplit.get_param(key, value)
                test_config.set_parameter(param_name, param_value)
            errors = compare_quality(test_config, base_config,
                                     lambda v, r: interpolate(test_params, v, r))

            line.update({'mae': str(round(errors["total_mae"], 5)), 'mse': str(round(errors["total_mse"], 5))})
            file.write(",".join(line.values()) + "\n")


def get_result_config(base_path: str, details: dict, run_id: int) -> HysplitResult:
    file, _ = hysplit_test.get_output_paths(base_path, details['name'], 0,
                                            hysplit_test.get_date_path_suffix(details["date"]))
    file = file.parent / f"data_{file.stem}_{run_id}.txt"
    config = HysplitResult(file, details["params"] if "params" in details else dict())
    return config


def compare_quality(test_result: HysplitResult, ground_truth_result: HysplitResult,
                    get_value, error_types: [str] = None):
    measure_types = error_types if error_types else ["mae", "mse"]
    test_result.fetch_results()
    ground_truth_result.fetch_results()
    return compute_errors(test_result, ground_truth_result, get_value, measure_types)


def compute_errors(dataset1: HysplitResult, dataset2: HysplitResult,
                   get_value, error_types: [str]) -> dict:
    dataset_fine, dataset_coarse = validate_datasets(dataset1, dataset2)
    error_measures = list()
    row_count = 0
    for row in dataset_coarse.results:
        row_count += 1
        relevant_fine_data = [Decimal(row["concentration"])
                              for row in get_matching_data(row, dataset_coarse, dataset_fine)]
        if len(relevant_fine_data) == 0:
            relevant_fine_data.append(Decimal(0))
        error_measures.append(get_error(Decimal(row["concentration"]), relevant_fine_data, get_value))
        if row_count % 1000 == 0:
            print(f"Completed row {row_count}")
    errors = dict()
    for measure_type in error_types:
        errors[f"total_{measure_type}"] = aggregate(error_measures, measure_type)
    return errors


def validate_datasets(dataset1, dataset2) -> tuple:
    # can also add span and center validation if needed
    spacing1 = get_width(dataset1.parameters[spacing_param_key])
    spacing2 = get_width(dataset2.parameters[spacing_param_key])
    dataset_fine, dataset_coarse = dataset1, dataset2
    if spacing1 > spacing2:
        dataset_fine, dataset_coarse = dataset2, dataset1
        spacing1, spacing2 = spacing2, spacing1
    if spacing2 / spacing1 != int(spacing2 / spacing1):
        raise Exception("Cannot compare: the smaller spacing does not divide the larger spacing")
    return dataset_fine, dataset_coarse


def get_matching_data(row: dict, dataset_coarse: HysplitResult, dataset_fine: HysplitResult) -> [dict]:
    fine_spacing = get_width(dataset_fine.parameters[spacing_param_key])
    coarse_spacing = get_width(dataset_coarse.parameters[spacing_param_key])
    grid_bounds = get_cell_bounds(row["latitude"], row["longitude"], coarse_spacing)
    sampling_rate = hysplit.get_sampling_rate_mins(dataset_coarse.parameters[sampling_param_key])
    relevant_data = list()
    for fine_row in dataset_fine.fetch_results():
        fine_row_bounds = get_cell_bounds(fine_row["latitude"], fine_row["longitude"], fine_spacing)
        if (grid_bounds["box"].overlaps(fine_row_bounds["box"])
                and is_within(get_time_range(row["timestamp"], sampling_rate), fine_row["timestamp"])):
            relevant_data.append(fine_row)
    return relevant_data


def get_width(width: str) -> Decimal:
    return Decimal(round(Decimal(width.split(" ")[0]), 4))


def get_time_range(time: str, increment_mins: int) -> (datetime, datetime):
    low = hysplit.get_date(time)
    high = low + timedelta(minutes=increment_mins)
    return low, high


def is_within(time_range: (datetime, datetime), timestamp: str) -> bool:
    return time_range[0] <= hysplit.get_date(timestamp) < time_range[1]


def get_cell_bounds(latitude: str, longitude: str, width: Decimal) -> dict:
    grid_center = Point(Decimal(latitude), Decimal(longitude))
    lower = Point(grid_center.latitude - width / 2, grid_center.longitude - width / 2)
    upper = Point(grid_center.latitude + width / 2, grid_center.longitude + width / 2)
    grid_bounds = {"center": grid_center,
                   "box": Box(lower, upper),
                   "width": width}
    return grid_bounds


interpolations = {
    "sampling": lambda val, rows: Decimal(val / len(rows))
}


def interpolate(params: [str], value: Decimal, rows: [Decimal]) -> Decimal:
    new_value = value
    for key in interpolations:
        if key in params:
            new_value = interpolations[key](new_value, rows)
    return new_value
