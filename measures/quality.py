import logging
from _decimal import Decimal
from pathlib import Path

from simulator import hysplit
from simulator.hysplit import Hysplit
from test_helpers import hysplit_test
from measures.error_measures import get_error, aggregate
from test_helpers.hysplit_test import bucket_macro
from util.parallel_processing import run_parallel_processes

logger = logging.getLogger("Main")
spacing_param_key = "%output_grids%::%spacing%"
sampling_param_key = "%output_grids%::%sampling%"
column_delimiter = ","
measure_types = ["mae", "mse", "mape"]


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


def measure_quality(test_details: dict, base_details: dict, process_count: int = 1,
                    base_path: str = "./debug/hysplit_out"):
    base_config = get_result_config(base_path, base_details, base_details["run_id"])
    base_config.fetch_results()
    measures_path = str(hysplit_test.get_quality_path(base_path, test_details).resolve())
    runtime_measures = hysplit_test.get_measures(test_details['name'], test_details["date"], base_path)

    for line in runtime_measures:
        logger.info(f"Started measuring for: {line['run_id']}")

        test_config = get_result_config(base_path, test_details, line["run_id"])
        test_configs = list()
        for key, value in line.items():
            param_name, param_value = hysplit.get_param(key, value)
            test_config.set_parameter(param_name, param_value)
        test_configs.append({"config": test_config, "details": line})

        run_parallel_processes(measure_bucket_qualities, test_configs, process_count, {
            "base_config": base_config,
            "get_value": lambda v, r: interpolate(line.keys(), v, r),
            "result_path": measures_path})
    logger.info(f"Written to: {measures_path}")


def measure_bucket_qualities(bucket: tuple, parameters: dict):
    bucket_id = bucket[0]
    test_runs = bucket[1]

    result_path = Path(parameters["result_path"].replace(bucket_macro, bucket_id))
    with result_path.open('a+') as file:
        file.write(column_delimiter.join(test_runs[0][1].keys() + measure_types))

    for run in test_runs:
        run_config = run["config"]
        run_config.fetch_results()
        error_aggregates, errors = compute_errors(run_config, parameters["base_config"], parameters["get_value"])

        run_details = run["details"]
        run_details.update(error_aggregates)
        with result_path.open("a+") as result_file:
            result_file.write(column_delimiter.join(run_details.values()) + "\n")
            result_file.flush()
        errors_dump_path = result_path.parent / f"errors_run-id_{run_details['run_id']}.txt"
        with errors_dump_path.open("w") as errors_file:
            errors_file.writelines([f"{error}\n" for error in errors])


def get_result_config(base_path: str, details: dict, run_id: int) -> HysplitResult:
    file, _ = hysplit_test.get_output_paths(base_path, details['name'], 0,
                                            hysplit_test.get_date_path_suffix(details["date"]))
    file = file.parent / f"{file.stem}_{run_id}.txt"
    config = HysplitResult(file, details["params"] if "params" in details else dict())
    return config


def compare_quality(test_result: HysplitResult, ground_truth_result: HysplitResult,
                    get_value, error_types: [str] = None):
    test_result.fetch_results()
    ground_truth_result.fetch_results()
    return compute_errors(test_result, ground_truth_result, get_value)


def compute_errors(dataset1: HysplitResult, dataset2: HysplitResult,
                   get_value) -> tuple:
    dataset_fine, dataset_coarse = validate_datasets(dataset1, dataset2)
    error_measures = list()
    row_count = 0
    for row in dataset_coarse.fetch_results():
        if row_count % 100000 == 0:
            logger.info(f"Starting row {row_count}")
        row_count += 1
        relevant_fine_data = [Decimal(row["concentration"])
                              for row in get_matching_data(row, dataset_coarse, dataset_fine)]
        if len(relevant_fine_data) == 0:
            relevant_fine_data.append(Decimal(0))
        error_measures.append(get_error(Decimal(row["concentration"]), relevant_fine_data, get_value))
    errors = dict()
    for measure_type in measure_types:
        errors[measure_type] = aggregate(error_measures, measure_type)
    return errors, error_measures


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
    row_latitude, row_longitude = Decimal(row["latitude"]), Decimal(row["longitude"])
    latitude_bounds = get_space_bounds(row_latitude, (coarse_spacing + fine_spacing) / 2)
    longitude_bounds = get_space_bounds(row_longitude, (coarse_spacing + fine_spacing) / 2)
    sampling_rate = hysplit.get_sampling_rate_mins(dataset_coarse.parameters[sampling_param_key])
    relevant_data = list()
    for fine_row in dataset_fine.fetch_results():
        time_diff_sec = (fine_row["timestamp"] - row["timestamp"]).total_seconds()
        if (time_diff_sec < 0 or time_diff_sec / 60 > sampling_rate
                or not check_bounds(Decimal(fine_row["latitude"]), latitude_bounds)
                or not check_bounds(Decimal(fine_row["longitude"]), longitude_bounds)):
            continue
        relevant_data.append(fine_row)
    return relevant_data


def get_width(width: str) -> Decimal:
    return Decimal(round(Decimal(width.split(" ")[0]), 4))


def get_space_bounds(value: Decimal, diff: Decimal):
    return value - diff, value + diff


def check_bounds(value: Decimal, bounds: tuple) -> bool:
    return bounds[0] < value < bounds[1]


interpolations = {
    "sampling": lambda val, rows: Decimal(val / len(rows))
}


def interpolate(params: [str], value: Decimal, rows: [Decimal]) -> Decimal:
    new_value = value
    for key in interpolations:
        if key in params:
            new_value = interpolations[key](new_value, rows)
    return new_value
