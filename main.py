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

x_min, y_min, x_max, y_max = 702200.0, 4309600.0, 702900.0, 4310200.0
unit = 10
# repo = SqlRepo()
farSite = FarSite(["%space_file%", "%initial_fire_shape%", "%start_time%",
                   "%end_time%", "%timestep%", "%distance_res%", "%perimeter_res%"])

first_names = ["Alice", "Bob", "Charles", "Darwin"]
last_names = ["Nunez", "Rowe", "Henderson", "Barry"]
diseases = ["covid-19", "tuberculosis", "asthma", "pneumonia", "chronic cough",
            "hay fever", "leukaemia", "influenza", "measles", "rubella"]
areas = ["lung", "lung", "lung", "lung", "lung", "lung", "blood", "throat", "lung", "bone marrow"]
hospitals = ['ACMH Hospital',
'AHMC Anaheim Regional Medical Center',
'AHMC Seton Medical Center',
'AHN Grove City',
'AHS Southcrest Hospital, LLC dba Hillcrest Hospital South',
'Abbeville General Hospital',
'Abbott Northwestern Hospital',
'Abrazo Arrowhead Campus',
'Abrazo Central Campus',
'Abrazo Scottsdale Campus',
'Abrazo West Campus',
'Acadia General Hospital (American Legion Hospital)',
'Acadian Medical Center',
'Addison Gilbert Hospital',
'Adena Regional Medical Center']


def run_experiment_te():
    for i in range(0, 515, 15):
        farSite.run({"%end_time%": f"05 04 {i:04d}"})


def run_experiment_ts():
    for i in range(1, 91, 3):
        farSite.run({"%timestep%": f"{i}"})


def run_experiment_pr():
    for i in range(1, 91, 3):
        dr = i if i < 5 else 5
        farSite.run({"%distance_res%": f"{dr}", "%perimeter_res%": f"{i}"})


def run_experiment_dr():
    perimeter_res = [1, 15, 30, 45, 60, 75, 90]
    for pr in perimeter_res:
        for dr in range(1, pr + 2, 2):
            farSite.run({"%perimeter_res%": f"{pr}", "%distance_res%": f"{dr}"})


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


def get_rows_person(count=10):
    end = datetime.now() - timedelta(days=365*50)
    start = datetime.now() - timedelta(days=365*110)
    delta = end - start
    int_delta = delta.days * 24 * 60 * 60 + delta.seconds
    new_rows = list()
    for i in range(0, count):
        name = random.choice(first_names) + " " + random.choice(last_names)
        birthdate = start + timedelta(seconds=random.randrange(int_delta))
        new_rows.append((name, birthdate.strftime("%Y-%m-%d")))
    return new_rows


def get_rows_disease(count=10):
    new_rows = list()
    for i in range(0, len(diseases)):
        new_rows.append((diseases[i], areas[i]))
    return new_rows


def get_rows_hospital(count=10):
    new_rows = list()
    for hospital in hospitals:
        new_rows.append((hospital, str(random.choice(range(30, 80)))))
    return new_rows


if __name__ == '__main__':
    # hysplit_test.default_test()
    # add_rows("disease", ("name", "affected_area"), get_rows_disease())
    # add_rows("person", ("name", "birthdate"), get_rows_person())
    # add_rows("hospital", ("name", "max_occupancy"), get_rows_hospital())
    # hysplit_test.total_run_time_test(attempts=3)
    # hysplit_test.emission_duration_test(attempts=3)
    # hysplit_test.locations_test(attempts=3)
    # hysplit_test.output_grid_sampling_test()
    # hysplit_test.pollutants_test()
    # hysplit_test.output_grid_spacing_test()
    # hysplit_test.total_run_time_test()
    # hysplit_test.output_grid_span_test()
    # hysplit_test.pollutants_test()
    # hysplit_test.output_grid_sampling_test()
    base_path = "/Users/sriramrao/code/farsite/farsite_driver/hysplit_out"
    data_files = [
        # f"{base_path}/span/2023-08-29_20-39/span_timings.txt",
        # f"{base_path}/pollutants_count/2023-08-26_22-55/pollutant_timings.txt",
        f"{base_path}/sampling/2023-08-30_02-07/sampling_timings.txt"]
    labels = [
        # ("Span (degrees)", "Time taken (seconds)"),
        # ("Pollutants (count)", "Time taken (seconds)"),
        ("Sample Duration (minutes)", "Time taken (seconds)")]
    plots.plot_all(data_files, labels)
