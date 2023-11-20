import platform  # to get the current CPU platform (arm or x86); used for sleeping to avoid overheading.
import time
from datetime import datetime
from pathlib import Path

import util.util
from simulator.hysplit import Hysplit, get_date_path_suffix
from test_helpers.test_data import slow_params
from util.util import RangeUtil


def default_test():
    hysplit = Hysplit()
    start = datetime.now()
    hysplit.run()
    end = datetime.now()
    duration = end - start
    print(f"Started at: {start}\nEnded at: {end}\nDuration: {duration.total_seconds()}")


def test(test_name: str, param_values: list, attempts: int, output_dir: str = "./debug/hysplit_out"):
    attempt_time_suffix = datetime.now().strftime('%Y-%m-%d_%H-%M')
    for attempt in range(0, attempts):
        output_path, measures_path = get_output_paths(output_dir, test_name, attempt, attempt_time_suffix)
        hysplit = Hysplit()
        total_count = len(param_values)

        with open(measures_path, "w") as measures_file:
            clean_keys = [key.upper().replace("%", "").replace("::", "__") for key in param_values[0][1].keys()]
            measures_file.writelines(f"ATTEMPT_ID,RUN_ID{','.join(clean_keys)},DURATION_S\n")
            for run_id, params in param_values:
                set_outputs(hysplit, output_path, run_id, params)
                print(f"{test_name} | Running: {run_id}, Total: {total_count}")
                start = datetime.now()
                hysplit.run(params)
                duration_s = (datetime.now() - start).total_seconds()
                print(f"Duration: {duration_s} s")
                clean_values = [value.replace("\n", " ") for value in params.values()]
                measures_file.writelines(f"{attempt},{run_id}{','.join(clean_values)},{duration_s}\n")
                sleep()
    return test_name, f"{output_dir}/{test_name}/{attempt_time_suffix}"


def locations_test(start=1, end=9, step=1, attempts=1):
    source_location = (40, -90, 50)
    location_step = 2
    values = list()
    for count in range(start, end + 1, step):
        locations = list()
        for source in range(1, count + 1):
            locations.append(" ".join([str(val + (source - 1) * location_step) for val in source_location]))
        values.append((str(len(locations)), {"%start_locations%": locations}))
    test("start_locations", values, attempts)


def grid_test(test_run=False):
    # For first initial runtime measurements, we vary the following parameters of Hysplit:
    #   - total_run_time (days of simulation)
    #   - output_grid.spacing[x, y] (the default values define a central point in LA and a rectangle surrounding it
    #                                that stretches +/- 0.5 in each direction (lat/long); the smaller the spacing the
    #                                more points are being calculated).
    #   - output_grid.sampling: "00 00 00 00 00\n00 00 00 00 00\n00 HH MM"

    # Parameter values with larger indexes are slower to calculate.
    total_run_time_values = ["1", "6", "12", "24", "36", "48", "60", "72", "96", "120", "180", "240"]
    output_grid_spacing_values = ["0.25", "0.2", "0.15", "0.1", "0.05", "0.02", "0.01", "0.005", "0.001"]
    output_grid_sampling_rates = ["08 00", "04 00", "02 00", "01 00", "00 30", "00 15", "00 10", "00 05"]

    # List slicing end ([:end]) of items per parameter. Unset when not testing.
    var_limit_for_testing = 2 if test_run else None

    hysplit = Hysplit()
    default_sampling = hysplit.get_defaults()["%output_grids%"][0]["%sampling%"]

    parameter_values = list()
    parameter_combination_id = 1
    for total_run_time in total_run_time_values[:var_limit_for_testing]:
        for output_grid_spacing in output_grid_spacing_values[:var_limit_for_testing]:
            for output_grid_sample_rate in output_grid_sampling_rates[:var_limit_for_testing]:
                sampling = default_sampling[:-5] + output_grid_sample_rate
                parameter_dict = {"%total_run_time%": total_run_time,
                                  "%output_grids%::%spacing%": f"{output_grid_spacing} {output_grid_spacing}",
                                  "%output_grids%::%sampling%": sampling}
                parameter_values.append((parameter_combination_id, parameter_dict))
                parameter_combination_id += 1

    # Run two rounds (or 'attempts') when testing, otherwise 5.
    test("grid_measurement", parameter_values, 2 if test_run else 5)


def coinciding_points_check():
    parameter_values = list()
    sampling_prefix = Hysplit().get_defaults()["%output_grids%"][0]["%sampling%"][:-5]
    parameter_dict = {"%%": f"",
                      "%output_grids%::%spacing%": f"0.05 0.05",
                      "%output_grids%::%sampling%": sampling_prefix + "01 00"}
    parameter_values.append((1, parameter_dict.copy()))
    parameter_dict["%output_grids%::%spacing%"] = f"0.1 0.1"
    parameter_values.append((2, parameter_dict.copy()))
    parameter_dict["%output_grids%::%spacing%"] = f"0.05 0.05"
    parameter_dict["%output_grids%::%sampling%"] = sampling_prefix + f"02 00"
    parameter_values.append((3, parameter_dict.copy()))
    parameter_dict["%output_grids%::%spacing%"] = f"0.1 0.1"
    parameter_values.append((4, parameter_dict.copy()))
    test("coinciding_points", parameter_values, 1)


def ground_truth():
    hysplit = Hysplit()
    default_sampling = hysplit.get_defaults()["%output_grids%"][0]["%sampling%"]
    sampling = default_sampling[:-5] + "01 00"
    parameter_dict = {"%output_grids%::%spacing%": f"0.001 0.001",
                      "%output_grids%::%sampling%": sampling}
    test("ground_truth", [(1, parameter_dict)], 1)


def total_run_time_test(start=24, end=10 * 24, step=24, attempts=1):
    test_values = list()
    for run_time in range(start, end + step, step):
        test_values.append((str(run_time), {"%total_run_time%": str(run_time)}))
    test("run_time", test_values, attempts)


def emission_duration_test(start=1, end=4 * 24, step=3, attempts=1):
    test_values = list()
    for duration in range(start, end + 1, step):
        test_values.append((str(duration), {"%emission_duration_hours%": str(duration)}))
    test("emission_duration", test_values, attempts)


def pollutants_test(start=0, end=4000, step=500, attempts=1):
    default_pollutant = {
        "%id%": "0000",
        "%emission_rate%": "50.0",
        "%emission_duration_hours%": "10.0",
        "%release_start%": "00 00 00 00 00"
    }
    default_deposition = "0.0 0.0 0.0\n0.0 0.0 0.0 0.0 0.0\n0.0 0.0 0.0\n0.0\n0.0"
    test_values = list()
    for count in range(start, end + 1, step):
        test_pollutants = list()
        next_end = count if count > 0 else 1
        for i in range(1, next_end + 1, 1):
            test_pollutant = default_pollutant.copy()
            test_pollutant["%id%"] = f"{i:04d}"
            test_pollutants.append(test_pollutant)
        test_values.append((next_end, {"%pollutants%": test_pollutants,
                                       "%deposition%": [default_deposition] * len(test_pollutants)}))
    test("pollutants_count", test_values, attempts)


def output_grid_centres_test():
    pass


def output_grid_spacing_test(start=0.1, end=3.0, step=0.1, attempts=1):
    default_grid = {
        "%centre%": "35.727513, -118.786136",
        "%spacing%": "0.01 0.01",
        "%span%": "180.0 360.0",
        "%dir%": "./",
        "%file%": "cdump",
        "%vertical_level%": "1\n50",
        "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 01 00",
    }
    test_values = [(0.01, {"%output_grids%": [default_grid.copy()]})]
    for space in util.util.RangeUtil.decimal_range(start, end + step, step):
        input_space = space if space > 0 else 0.001
        default_grid["%spacing%"] = f"{input_space} {input_space}"
        test_values.append((space, {"%output_grids%": [default_grid.copy()]}))
    return test("spacing", test_values, attempts)


def output_grid_span_test(start=0.0, lat_end=180.0, long_end=360.0, step=10, attempts=1):
    default_grid = {
        "%centre%": "35.727513, -118.786136",
        "%spacing%": "0.1 0.1",
        "%span%": "180.0 360.0",
        "%dir%": "./",
        "%file%": "cdump",
        "%vertical_level%": "1\n50",
        "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 01 00",
    }

    test_values = list()
    for span in RangeUtil.decimal_range(start, lat_end + step, step):
        input_span = span if span > 0 else 1.0
        default_grid["%span%"] = f"{input_span} {input_span}"
        test_values.append((input_span, {"%output_grids%": [default_grid.copy()]}))

    for long_span in RangeUtil.decimal_range(lat_end, long_end + step, step * 2):
        default_grid["%span%"] = f"{lat_end} {long_span}"
        test_values.append((long_span, {"%output_grids%": [default_grid.copy()]}))
    return test("span", test_values, attempts)


def output_grid_sampling_test(start=0, end=60, step=5, attempts=1):
    param_key = "%output_grids%"
    default_grid = {
        "%centre%": "35.727513, -118.786136",
        "%spacing%": "0.1 0.1",
        "%span%": "10.0 10.0",
        "%dir%": "./",
        "%file%": "cdump",
        "%vertical_level%": "1\n50",
        "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 01 00",
    }
    test_values = list()  # [(0.01, {param_key: [default_grid.copy()]})]
    for rate in range(start, end + 1, step):
        input_rate = rate if rate > 0 else 1
        default_grid["%sampling%"] = f"00 00 00 00 00\n00 00 00 00 00\n00 00 {input_rate:02d}"
        test_values.append((rate, {param_key: [default_grid.copy()]}))
    for rate in range(2, 50, 4):
        default_grid["%sampling%"] = f"00 00 00 00 00\n00 00 00 00 00\n00 {rate:02d} 00"
        test_values.append((rate * 60, {param_key: [default_grid.copy()]}))
    return test("sampling", test_values, attempts)


def slow_hysplit_run():
    parameter_dict = [(1, slow_params)]
    return test("slow_run", parameter_dict, 1)


def get_measures(test_name: str, test_time: str, base_path: str):
    measurements_file = (get_test_prefix(base_path, test_name,
                                         get_date_path_suffix(test_time)) / "runtime_measurements.csv")
    with (open(measurements_file, 'r') as measures_file):
        attributes = measures_file.readline().strip('\n').replace("__", "::").split(",")
        for line in measures_file:
            values = line.strip('\n').split(',')
            measure = dict()
            for i in range(0, len(values)):
                measure[attributes[i].lower()] = values[i]
            yield measure


measures_meta_attributes = {"attempt_id", "run_id", "duration_s"}


def get_measures_meta_attributes() -> set:
    return measures_meta_attributes


def get_test_prefix(base_path: str, test_name: str, test_time: str) -> Path:
    return Path(base_path).resolve() / test_name / test_time


def set_outputs(hysplit: Hysplit, output_path: Path, run_id: int, run_params: dict) -> None:
    output_grids = hysplit.get_parameter("%output_grids%") if "%output_grids%" not in run_params.keys() \
        else run_params["%output_grids%"]
    output_grids[0]["%dir%"] = str(output_path.parent) + "/"
    output_grids[0]["%file%"] = f"{output_path.stem}_{str(run_id).replace('.', '-')}"
    hysplit.set_parameter("%output_grids%", output_grids)


def get_output_paths(directory: str, test_name: str, attempt: int, suffix: str) -> (Path, Path):
    base_path = Path(f"{directory}/{test_name}/{suffix}")
    output_path = base_path / str(attempt) / "dump"
    measures_path = base_path / f"runtime_measurements_{attempt}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path, measures_path


def get_quality_path(base_path: str, test_details: dict) -> Path:
    date_str = get_date_path_suffix(test_details["date"])
    current_date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return Path(base_path) / test_details['name'] / date_str / f"measures_{current_date_str}.csv"


def sleep():
    if platform.processor() != "arm" and platform.system() != "Linux":
        # Sleep when not on arm to avoid overheating. Also, when running on Linux we assume to run on a
        # sufficiently cooled server machine.
        time.sleep(5)
