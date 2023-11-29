import argparse

import log
from driver import Driver
from measures import quality
from repo.edb_repo import EdbRepo
from test_helpers.hysplit_test import *


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
    args = parser.parse_args()
    defaults = {"%output_grids%::%spacing%": "0.001 0.001",
                "%output_grids%::%sampling%": "00 00 05",
                "%grid_center%": "34.12448, -118.40778",
                "%span%": "5.0 5.0"}
    logger.info(f"Name: {args.name}, Date: {args.date}, Run ID: {args.runid}")
    quality.measure_quality(
        test_details={"name": args.name, "date": args.date, "thread_name": args.threadname, "params": defaults},
        base_details={"name": args.name, "date": args.date, "thread_name": args.threadname, "params": defaults, "run_id": args.runid})


if __name__ == '__main__':
    log.init()
    quality_check()
