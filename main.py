import argparse

import log
import settings
from driver import Driver
from measures import quality, quality_plot
from repo.edb_repo import EdbRepo
from test_helpers.hysplit_test import *
from util import files


def test_drive(sleep_seconds = settings.DRIVER_SLEEP_SECONDS):
    repo = EdbRepo()
    simulation_driver = Driver(repo, sleep_seconds)
    simulation_driver.set_planner("hysplit", "plan.planner.GreedyPlanner",
                                  repo.get_test_data("hysplit_test_data"))
    simulation_driver.run()


def quality_check():
    parser = argparse.ArgumentParser(description="Get quality measures.")
    parser.add_argument("-n", "--name", required=True, help="Name of the (directory of the) test run.")
    parser.add_argument("-d", "--date", required=True, help="Datetime (yyyy-MM-dd_HH-mm) when the test was run.")
    parser.add_argument("-r", "--runid", required=True,
                        help="Run ID of the test that should be considered ground truth")
    parser.add_argument("-t", "--threadname", default="", help="Name of the thread that ran the test.")
    parser.add_argument("-b", "--basepath", default="./debug/hysplit_out", help="Base directory of the test.")
    parser.add_argument("-i", "--infilename", default="dump", help="Name prefix for files with generator data.")
    args = parser.parse_args()
    defaults = {"%output_grids%::%spacing%": "0.01 0.01",
                "%output_grids%::%sampling%": "00 00 05",
                "%grid_center%": "34.12448, -118.40778",
                "%span%": "0.5 0.5"}
    logger.info(f"Name: {args.name}, Date: {args.date}, Run ID: {args.runid}")
    quality.measure_quality(
        test_details={"name": args.name, "date": args.date, "name_prefix": args.infilename,
                      "thread_name": args.threadname, "params": defaults},
        base_details={"name": args.name, "date": args.date, "name_prefix": args.infilename,
                      "thread_name": args.threadname, "params": defaults, "run_id": args.runid},
        base_path=args.basepath)


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
    summary_file = Path("/Users/sriramrao/code/simulation/simulation_driver/debug/measures/errors_summary.csv")
    quality_plot.plot_measures("/Users/sriramrao/code/simulation/simulation_driver/debug/measures/measures_merged.csv",
                               str(summary_file), False)


if __name__ == '__main__':
    log.init()
    grid_test()
    # driver_data_queries_test()
