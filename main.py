import argparse

import log
import settings
from driver import Driver
from measures import quality, quality_plot, compute
from repo.edb_repo import EdbRepo
from test_helpers import hysplit_test
from test_helpers.hysplit_test import *
from util import files, parallel_processing


def test_drive(sleep_seconds=settings.DRIVER_SLEEP_SECONDS):
    repo = EdbRepo()
    simulation_driver = Driver(repo, sleep_seconds)
    # simulation_driver.set_planner("hysplit", "plan.planner.GreedyPlanner",
    #                               repo.get_test_data("hysplit_test_data"))
    simulation_driver.run()


def quality_check():
    parser = argparse.ArgumentParser(description="Get quality measures.")
    parser.add_argument("-n", "--name", default="grid_measurement", help="Name of the (directory of the) test run.")
    parser.add_argument("-d", "--date", required=True, help="Datetime (yyyy-MM-dd_HH-mm) when the test was run.")
    parser.add_argument("-r", "--runid", required=True,
                        help="Run ID of the test that should be considered ground truth")
    parser.add_argument("-t", "--threadname", default="MainProcess", help="Name of the thread that ran the test.")
    parser.add_argument("-b", "--basepath", default="./debug/hysplit_out", help="Base directory of the test.")
    parser.add_argument("-i", "--infilename", default="data_dump", help="Name prefix for files with generated data.")
    args = parser.parse_args()
    defaults = {"%output_grids%::%spacing%": "0.01 0.01",
                "%output_grids%::%sampling%": "00 00 01",
                "%grid_center%": "34.12448, -118.40778",
                "%span%": "0.5 0.5"}
    logger.info(f"Name: {args.name}, Date: {args.date}, Run ID: {args.runid}")
    config = {"name": args.name, "date": args.date, "name_prefix": args.infilename,
              "thread_name": args.threadname, "params": defaults, "run_id": args.runid}
    quality.measure_quality(test_details=config, base_path=args.basepath)


def get_measure_files(path: Path) -> [Path]:
    contents = path.glob("measures_*.csv")
    measure_files = [c for c in contents if c.is_file()]
    return measure_files


def collate_measures():
    parser = argparse.ArgumentParser(description="Collate measures_*.csv files in the given path")
    parser.add_argument("-p", "--path", required=True, help="Path to directory with measures.csv files.")
    args = parser.parse_args()
    measures_path = Path(args.path).resolve()
    measure_files = get_measure_files(measures_path)
    files.merge(measure_files, measures_path / "measures_merged.csv")


def plot_qualities():
    durations_path = "/Users/sriramrao/code/simulation/simulation_driver/debug/measures/"
    summary_file = Path("/Users/sriramrao/code/simulation/simulation_driver/debug/errors_summary.csv")
    quality_plot.plot_measures(durations_path, str(summary_file), True)


def recompute_errors(errors_path: str):
    error_files = Path(errors_path).resolve().glob("errors_run_*.csv")
    summary_file = Path(errors_path) / "error_summary.csv"
    parallel_processing.run_processes(compute.batch_recompute, list(error_files),
                                      static_params={"summary_file": str(summary_file)})


def test_errors():
    defaults = {"%output_grids%::%spacing%": "0.01 0.01",
                "%output_grids%::%sampling%": "00 00 01",
                "%grid_center%": "34.12448, -118.40778"}
    file = Path("/Users/sriramrao/code/simulation/simulation_driver/"
                "debug/hysplit_out/measures/2023-12-24/").resolve()
    base_config = quality.HysplitResult(file / "data_dump_140.csv", defaults)
    test_values = defaults.copy()
    test_values["%output_grids%::%sampling%"] = "00 00 02"
    test_config = quality.HysplitResult(file / "data_dump_139.csv", test_values)

    # quality.measure_quality(
    #     test_details={"name": "grid_measurement", "date": "2023-11-26_23-16", "name_prefix": "data_dump",
    #                   "thread_name": "", "params": defaults},
    #     base_details={"name": "grid_measurement", "date": "2023-11-26_23-16", "name_prefix": "data_dump",
    #                   "thread_name": "", "params": defaults, "run_id": 1},
    #     base_path="./debug/hysplit_out/")
    keys = "attempt_id,run_id,total_run_time,output_grids::spacing,output_grids::sampling,duration_s".split(",")
    error_summary, error_rows = quality.compute_errors(test_config, base_config)
    logger.info(f"Errors: {error_summary}")


def test_and_measure():
    parser = argparse.ArgumentParser(description="Run grid tests and quality measurements.")
    parser.add_argument("-d", "--date", required=True, help="Datetime (yyyy-MM-dd_HH-mm)")
    parser.add_argument("-r", "--runid", required=True,
                        help="Run ID of the test that should be considered ground truth")
    defaults = {"%output_grids%::%spacing%": "0.01 0.01",
                "%output_grids%::%sampling%": "00 00 05",
                "%grid_center%": "34.12448, -118.40778"}
    args = parser.parse_args()

    logger.info(f"Date: {args.date}, Run ID: {args.runid}")
    logger.info(f"Beginning grid test, date: {args.date}")
    hysplit_test.grid_test(time_suffix=args.date)

    logger.info(f"Beginning quality measurements, date: {args.date}, base runID: {args.runid}")
    details = {"name": "grid_measurement", "date": args.date, "name_prefix": "data_dump",
               "thread_name": "MainProcess", "params": defaults, "run_id": args.runid}
    quality.measure_quality(test_details=details, base_path=args.basepath)
    logger.info(f"Execution complete")


if __name__ == '__main__':
    log.init()
    # test_drive()
    # test_errors()
    # plot_qualities()
    # driver_data_queries_test()
    # hysplit_test.default_test()
    # plot_qualities()
    # test_errors()
    quality_check()
