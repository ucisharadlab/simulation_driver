import os
from datetime import datetime, timedelta
import random

import driver
from cell_mappings import generate_cell_mapping
import hysplit_test
import plots
from repo.edb_repo import EdbRepo
from repo.sql_repo import SqlRepo
from simulator.farsite import FarSite
from simulator.hysplit import Hysplit


def read_latency(read_path: str, project: str):
    filename = project + '_Timings.txt'
    # for file in df_file_list:
    file = os.path.join(read_path, filename)
    with open(file, 'r') as f:
        lines = f.readlines()
    measures = [lines[9], lines[10], lines[11], lines[14], lines[15], lines[16], lines[-1]]
    measures = [s.strip().split(":")[1] for s in measures]
    measures[-1] = measures[-1].split(" Seconds")[0]
    # print(time)
    return measures


def read_experiment_latencies(root_dir: str):
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            print(read_latency(os.path.join(subdir, file), "Burn"))


def get_start_cell_id(geography_file: str) -> int:
    return 0


def get_cell_id_results(input_file: str, cell_mapping_file: str) -> dict:
    cell_id = get_start_cell_id(input_file)
    mappings = open(cell_mapping_file, 'r').readlines()
    results = dict()
    row_num = 0
    for row in mappings:
        row_num += 1
        if row_num == 1:
            continue
        for cell in row.split(',')[:-1]:
            results[cell_id] = True if cell == '1' else False
            cell_id += 1
    return results


def test_drive():
    db_repo = EdbRepo()
    driver.run(db_repo)


def cleanup():
    repo = EdbRepo()
    repo.remove_simulator("FireSim")
    repo.remove_simulated_columns("fire_presence", "fire_presence")
    print("clean")


def start_driver():
    cleanup()
    repo = EdbRepo()
    repo.add_simulator("FireSim", "FarSite", "presence", "{\"time_extent\": 60, \"\": \"\"}")
    repo.add_simulated_columns("fire_presence", "fire_map", "cell_id, endtime", "fire_presence", "presence")
    test_drive()
    print("done")


def add_rows(table: str, values: tuple, rows: list):
    if len(rows) < 1:
        return
    is_first_processed = False
    command = f"INSERT INTO {table} ({','.join(values)}) VALUES "
    for row in rows:
        command += ",\n" if is_first_processed else ""
        if not is_first_processed:
            is_first_processed = True
        line = "'" + "', '".join(row) + "'"
        command += f"({line})"

    repo = SqlRepo()
    repo.execute(command)


if __name__ == '__main__':
    # spacing_test_name, spacing_dir = hysplit_test.output_grid_spacing_test(attempts=10)
    # span_name, span_dir = hysplit_test.output_grid_span_test(attempts=10)
    # sampling_name, sampling_dir = hysplit_test.output_grid_sampling_test(attempts=10)
    # pollutants_name, pollutants_dir = hysplit_test.pollutants_test(attempts=2)
    # data_paths = [
    #     ("spacing", "./debug/hysplit_out/spacing/2023-09-13_23-00/", 10),
        # ("span", "./debug/hysplit_out/span/2023-09-14_03-50/", 10),
        # ("sampling", "./debug/hysplit_out/sampling/2023-09-14_04-44/", 10),
        # (pollutants_name, pollutants_dir, 10)
    # ]
    # labels = [
    #     ("Spatial Resolution (Spacing)", "Simulation Time (seconds)"),
        # ("Spatial Extent (Span in degrees)", "Simulation Time (seconds)"),
        # ("Time Resolution (Sampling duration in minutes)", "Simulation Time (seconds)"),
        # ("Pollutants Count", "Simulation Time (seconds)")
    # ]
    # plots.plot_all(data_paths, labels)

    # hysplit_test.locations_test()
    # hysplit_test.pollutants_test()

    # hysplit_test.grid_test(False)  # full run
    hysplit_test.grid_test(True)  # fast run
