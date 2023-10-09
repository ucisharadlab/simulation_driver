import os
import time
from datetime import datetime

from repo.edb_repo import EdbRepo
from simulator.hysplit import Hysplit


def default_test():
    hysplit = Hysplit("")
    start = datetime.now()
    hysplit.run()
    end = datetime.now()
    duration = end - start
    print(f"Started at: {start}\nEnded at: {end}\nDuration: {duration.total_seconds()}")


def test(test_name: str, param_values: list, attempts: int, output_dir: str = "./debug/hysplit_out"):
    attempt_time_suffix = datetime.now().strftime('%Y-%m-%d_%H-%M')
    for attempt in range(0, attempts):
        output_path, timings_path = get_output_paths(output_dir, test_name, attempt, attempt_time_suffix)
        hysplit = Hysplit("")
        os.makedirs(os.path.split(output_path)[0], exist_ok=True)
        total_count = len(param_values)
        durations = list()
        for index, param in enumerate(param_values):
            set_outputs(hysplit, output_path, param)
            print(f"Running: {index + 1}, Total: {total_count} | {test_name}: {param[0]}")
            start = datetime.now()
            hysplit.run(param[1])
            duration = datetime.now() - start
            print(f"Duration: {duration.total_seconds()}")
            durations.append(str(param[0]) + "\t" + str(duration.total_seconds()) + "\n")
            time.sleep(5)
        with open(timings_path, "w") as timings_file:
            timings_file.writelines(durations)
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


def start_locations_spacing_test():
    # from
    pass


def total_run_time_test(start=24, end=10*24, step=24, attempts=1):
    test_values = list()
    for time in range(start, end + step, step):
        test_values.append((str(time), {"%total_run_time%": str(time)}))
    test("run_time", test_values, attempts)


def emission_duration_test(start=1, end=4*24, step=3, attempts=1):
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
        "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 00 59",
    }
    test_values = [(0.01, {"%output_grids%": [default_grid.copy()]})]
    for space in decimal_range(start, end + step, step):
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
    for span in decimal_range(start, lat_end + step, step):
        input_span = span if span > 0 else 1.0
        default_grid["%span%"] = f"{input_span} {input_span}"
        test_values.append((input_span, {"%output_grids%": [default_grid.copy()]}))

    for long_span in decimal_range(lat_end, long_end + step, step * 2):
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


def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment
# check input data grids, pollutants


def set_outputs(hysplit: Hysplit, output_path: str, run_param: tuple) -> None:
    output_dir, output_file = os.path.split(output_path)
    output_grids = hysplit.get_parameter("%output_grids%") if "%output_grids%" not in run_param[1].keys() \
        else run_param[1]["%output_grids%"]
    output_grids[0]["%dir%"] = output_dir + "/"
    output_grids[0]["%file%"] = f"{output_file}_{str(run_param[0]).replace('.', '-')}"
    hysplit.set_parameter("%output_grids%", output_grids)


def get_output_paths(directory: str, test_name: str, attempt: int, suffix: str) -> tuple:
    base_path = f"{directory}/{test_name}/{suffix}"
    output_path = f"{base_path}/{attempt}/dump"
    timings_path = f"{base_path}/timings_{attempt}.txt"
    return output_path, timings_path
