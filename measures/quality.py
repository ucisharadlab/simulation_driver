import logging
import multiprocessing
from _decimal import Decimal
from datetime import datetime, timedelta
from multiprocessing import current_process
from pathlib import Path

from measures.error_measures import get_error, aggregate
from simulator import hysplit
from simulator.hysplit import Hysplit
from test_helpers import hysplit_test
from test_helpers.hysplit_test import bucket_macro
from util import files
from util.parallel_processing import run_processes

logger = logging.getLogger()
logger.setLevel(logging.INFO)
spacing_param_key = "%output_grids%::%spacing%"
sampling_param_key = "%output_grids%::%sampling%"
measure_types = ["mae", "mse", "mape"]
frechet_deviation = 0.5


def set_logger():
    global logger
    logger = logging.getLogger(current_process().name)
    logger.setLevel(logging.INFO)


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


def measure_quality(test_details: dict, process_count: int = multiprocessing.cpu_count(),
                    base_path: str = "./debug/hysplit_out", base_details: dict = None):
    base_details = base_details if base_details else test_details
    base_config = get_result_config(base_path, base_details, base_details["run_id"])
    base_config.fetch_results()
    measures_path = hysplit_test.get_quality_path(base_path, test_details).resolve()
    measures_path.parent.mkdir(parents=True, exist_ok=True)
    measures_path_str = str(measures_path)
    test_configs = prepare_test_config(test_details, base_path)

    run_processes(measure_bucket_qualities, test_configs, process_count, {
        "base_config": base_config,
        "result_path": measures_path_str})

    measure_files = list()
    for i in range(0, process_count):
        measure_files.append(Path(str(measures_path).replace(bucket_macro, str(i))))
    merged_file = Path(measures_path_str.replace(f"_{bucket_macro}", ""))
    files.merge(measure_files, merged_file)
    logger.info(f"Written to: {merged_file}")


def prepare_test_config(test_details: dict, base_path: str):
    test_configs = list()
    for line in hysplit_test.get_measures(test_details["name"], test_details["date"],
                                          test_details["thread_name"], base_path):
        test_config = get_result_config(base_path, test_details, line["run_id"])
        for key, value in line.items():
            param_name, param_value = hysplit.get_param(key, value)
            test_config.set_parameter(param_name, param_value)
            test_config.parameters[param_name] = param_value
        test_configs.append({"config": test_config, "details": line})
    return test_configs


def measure_bucket_qualities(test_runs: list, parameters: dict):
    if not test_runs or len(test_runs) == 0:
        return

    set_logger()
    result_path = Path(parameters["result_path"].replace(bucket_macro, "0"))  # str(current_process().bucket_id)))
    files.write_list_to_line(result_path, (list(test_runs[0]["details"].keys()) + measure_types))

    for i, run in enumerate(test_runs):
        run_details = run["details"]
        run_id = run_details["run_id"]
        logger.info(f"({i + 1}/{len(test_runs)}) Comparing run: {run_id}")
        run["config"].fetch_results()
        try:
            start = datetime.now()
            error_aggregates, errors = compute_errors(run["config"], parameters["base_config"])
            duration = (datetime.now() - start).total_seconds()
            logger.info(f"Duration: {duration} seconds")

            error_measures = {key: str(round(error, 5)) for key, error in error_aggregates.items()}
            run_details.update(error_measures)
            files.write_list_to_line(result_path, run_details.values())
            errors_file = result_path.parent / f"errors_run_{run_id}.json"
            files.write_json(errors_file, errors)
            logger.info(f"Completed run: {run_id}, errors file: {errors_file}")
        except Exception as e:
            logger.error("Could not compute errors for %s", run_id)
            logger.exception(e, exc_info=True)
            continue


def get_result_config(base_path: str, details: dict, run_id: int) -> HysplitResult:
    _, file, _ = hysplit_test.get_output_paths(base_path, details["name"], 0,
                                               details["date"], details["thread_name"], details["name_prefix"])
    file = file.parent / f"{file.stem}_{run_id}.txt"
    config = HysplitResult(file, details["params"] if "params" in details else dict())
    return config


def compute_errors(dataset1: HysplitResult, dataset2: HysplitResult) -> tuple:
    dataset_fine, dataset_coarse, sampling_multiplier, node_count = validate_datasets(dataset1, dataset2)
    fine_spacing = get_width(dataset_fine.parameters[spacing_param_key])
    coarse_sampling = hysplit.get_sampling_rate_mins(dataset_coarse.parameters[sampling_param_key])
    error_measures = list()
    row_count = 0
    grouped_fine_data = group_by_time(dataset_fine)
    for row in dataset_coarse.fetch_results():
        error_row = {"row_value": row["concentration"]}
        shifted_errors = list()
        for timestamp in get_frechet_times(row["timestamp"], coarse_sampling):
            relevant_fine_data = [Decimal(r["concentration"]) for r in
                                  get_matching_data(row, timestamp, dataset_coarse, fine_spacing, grouped_fine_data)]
            row_errors = get_error(Decimal(row["concentration"]) / sampling_multiplier, relevant_fine_data)
            row_errors["absolute"] = row_errors["absolute"] * node_count
            shifted_errors.append(row_errors)
        frechet_errors = dict()
        for key in shifted_errors[0].keys():
            frechet_errors[key] = min(x[key] for x in shifted_errors)

        error_row["errors"] = frechet_errors
        error_measures.append(error_row)
        row_count += 1
        if row_count % 100000 == 0:
            logger.info(f"Row: {row_count}")
    errors = dict()
    for measure_type in measure_types:
        errors[measure_type] = aggregate([row["errors"] for row in error_measures], measure_type)
    return errors, error_measures


def validate_datasets(dataset1, dataset2) -> tuple:
    spacing1 = get_width(dataset1.parameters[spacing_param_key])
    sampling1 = hysplit.get_sampling_rate_mins(dataset1.parameters[sampling_param_key])
    spacing2 = get_width(dataset2.parameters[spacing_param_key])
    sampling2 = hysplit.get_sampling_rate_mins(dataset2.parameters[sampling_param_key])
    dataset_fine, dataset_coarse = dataset1, dataset2
    if spacing1 > spacing2 or sampling1 > sampling2:
        dataset_fine, dataset_coarse = dataset2, dataset1
        spacing1, spacing2 = spacing2, spacing1
        sampling1, sampling2 = sampling2, sampling1
    space_multiplier = spacing2 / spacing1
    sampling_multiplier = Decimal(sampling2 / sampling1)
    if (space_multiplier != spacing2 // spacing1
            or sampling_multiplier != sampling2 // sampling1):
        raise Exception("Cannot compare: the finer parameter does not divide the coarser parameter")
    multiplier = sampling_multiplier * space_multiplier
    logger.info(f"Multiplier: {multiplier}, Sampling Multiplier: {sampling_multiplier}\nCoarse Sampling: {sampling2}, Fine Sampling: {sampling1}\n"
                f"Coarse Spacing: {spacing2}, Fine Spacing: {spacing1}")
    return dataset_fine, dataset_coarse, sampling_multiplier, multiplier


def group_by_time(dataset: HysplitResult) -> dict:
    grouped_data = dict()
    for row in dataset.fetch_results():
        timestamp = row["timestamp"]
        if timestamp not in grouped_data:
            grouped_data[timestamp] = list()
        grouped_data[timestamp].append(row)
    return grouped_data


def get_matching_data(row: dict, row_timestamp: datetime, dataset_coarse: HysplitResult, fine_spacing: Decimal, grouped_data: dict) -> [dict]:
    coarse_spacing = get_width(dataset_coarse.parameters[spacing_param_key])
    row_latitude, row_longitude = Decimal(row["latitude"]), Decimal(row["longitude"])
    latitude_bounds = get_space_bounds(row_latitude, (coarse_spacing + fine_spacing) / 2)
    longitude_bounds = get_space_bounds(row_longitude, (coarse_spacing + fine_spacing) / 2)
    sampling_rate = hysplit.get_sampling_rate_mins(dataset_coarse.parameters[sampling_param_key])
    relevant_data = list()

    times = list(grouped_data.keys())
    times.sort()
    for timestamp in times:
        time_diff_sec = (timestamp - row_timestamp).total_seconds()
        if time_diff_sec / 60 >= sampling_rate:  # assumption: rows in hysplit result are ordered by time
            break
        if time_diff_sec < 0:
            continue
        for fine_row in grouped_data[timestamp]:
            if not (check_bounds(Decimal(fine_row["latitude"]), latitude_bounds)
                    and check_bounds(Decimal(fine_row["longitude"]), longitude_bounds)):
                continue
            relevant_data.append(fine_row)

    if len(relevant_data) == 0:
        relevant_data.append({"concentration": 0.0})
    return relevant_data


def get_frechet_times(timestamp: datetime, sampling_interval: int) -> [datetime]:
    deviation = timedelta(minutes=sampling_interval * frechet_deviation)
    return [timestamp - deviation, timestamp, timestamp + deviation]


def get_width(width: str) -> Decimal:
    return Decimal(round(Decimal(width.split(" ")[0]), 4))


def get_space_bounds(value: Decimal, diff: Decimal):
    return value - diff, value + diff


def check_bounds(value: Decimal, bounds: tuple) -> bool:
    return bounds[0] < value < bounds[1]
