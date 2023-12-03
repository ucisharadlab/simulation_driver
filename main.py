import argparse

import log
import plots
from driver import Driver
from measures import quality
from repo.edb_repo import EdbRepo
from test_helpers.hysplit_test import *
from util import files


def test_drive(sleep_seconds):
    repo = EdbRepo()
    simulation_driver = Driver(repo, sleep_seconds)
    simulation_driver.set_planner("hysplit", "plan.planner.GreedyPlanner",
                                  repo.get_test_data("hysplit_test_data"))
    simulation_driver.run()


def quality_check():
    parser = argparse.ArgumentParser(description="Get quality measures.")
    parser.add_argument("-n", "--name", required=True, help="Name of the (directory of the) test run.")
    parser.add_argument("-d", "--date", required=True, help="Datetime (yyyy-MM-dd_HH-mm) when the test was run.")
    parser.add_argument("-r", "--runid", required=True, help="Run ID of the test that should be considered ground truth")
    parser.add_argument("-t", "--threadname", default="", help="Name of the thread that ran the test.")
    parser.add_argument("-b", "--basepath", default="./debug/hysplit_out", help="Base directory of the test.")
    parser.add_argument("-i", "--infilename", default="dump", help="Name prefix for files with generator data.")
    args = parser.parse_args()
    defaults = {"%output_grids%::%spacing%": "0.001 0.001",
                "%output_grids%::%sampling%": "00 00 05",
                "%grid_center%": "34.12448, -118.40778",
                "%span%": "5.0 5.0"}
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


if __name__ == '__main__':
    log.init()
    # 852,
    # compute.recompute_errors(Path("/Users/sriramrao/code/simulation/simulation_driver/debug/test/errors_run_63.json"),
    #                          Path("/Users/sriramrao/code/simulation/simulation_driver/debug/measures/errors_summary.csv"))
    summary_file = Path("/Users/sriramrao/code/simulation/simulation_driver/debug/measures/errors_summary.csv")
    # csv_files = Path("/Users/sriramrao/code/simulation/simulation_driver/debug/measures/errors_run_*.csv")

    # util.parallel_processing.run_processes(compute.batch_recompute, csv_files,
    #                                        process_count=multiprocessing.cpu_count() - 2,
    #                                        static_params={"summary_file": summary_file})
    # files.merge(files.get_files_like(summary_file.parent, summary_file.stem + "_*" + summary_file.suffix),
    #             summary_file)

    plots.plot_measures("/Users/sriramrao/code/simulation/simulation_driver/debug/measures/measures_merged.csv",
                        str(summary_file))
    # collate_measures()
    # quality_check()

