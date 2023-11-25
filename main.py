import logging

import settings
from driver import Driver
from measures import quality
import plots
from repo.edb_repo import EdbRepo
from test_helpers.hysplit_test import *


def init():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[logging.FileHandler(get_log_file_name()), logging.StreamHandler()]
    )


def get_log_file_name():
    current_date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = Path(settings.LOG_FILE_PATH).resolve() / f"driver_{current_date_str}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def test_drive(sleep_seconds):
    repo = EdbRepo()
    simulation_driver = Driver(repo, sleep_seconds)
    simulation_driver.set_planner("hysplit", "plan.planner.GreedyPlanner",
                                  repo.get_test_data("hysplit_test_data"))
    simulation_driver.run()


def quality_check():
    defaults = {"%output_grids%::%spacing%": "0.1 0.1",
                "%output_grids%::%sampling%": "00 00 30",
                "%grid_center%": "35.727513, -118.786136",
                "%span%": "180.0 360.0"}
    quality.measure_quality(
        test_details={"name": "sampling", "date": "2023-09-14 04:44", "params": defaults},
        base_details={"name": "sampling", "date": "2023-09-14 04:44", "params": defaults, "run_id": 120})


if __name__ == '__main__':
    init()
    # test_drive(settings.DRIVER_SLEEP_SECONDS)
    # quality_check()
    config = {"test_name": "coinciding_points", "test_time": "2023-11-16_15-47",
              "measure_param": "OUTPUT_GRIDS__SAMPLING", "measure_time": "2023-11-21_00-25",
              "label": "Sampling", "parse": parsers["sampling"],
              # "constants": [("TOTAL_RUN_TIME", "6"), ("OUTPUT_GRIDS__SPACING", "0.005 0.005")]
              "constants": [
                  {"LABEL": "run_6_space_005", "TOTAL_RUN_TIME": "6", "COLOR": "red",
                   "OUTPUT_GRIDS__SPACING": "0.05 0.05"},
                  {"LABEL": "run_1_space_01", "TOTAL_RUN_TIME": "1", "COLOR": "blue",
                   "OUTPUT_GRIDS__SPACING": "0.01 0.01"},
                  {"LABEL": "run_6_space_1", "TOTAL_RUN_TIME": "6", "COLOR": "green",
                   "OUTPUT_GRIDS__SPACING": "0.1 0.1"},
                  {"LABEL": "run_1_space_25", "TOTAL_RUN_TIME": "1",  "COLOR": "black",
                   "OUTPUT_GRIDS__SPACING": "0.25 0.25"},
              ]}
    # "constants": [("TOTAL_RUN_TIME", "6"), ("OUTPUT_GRIDS__SAMPLING", "00 00 00 00 00 00 00 00 00 00 00 00 05")]
    # Notes: normalize errors, more data points?

    plots.plot_qualities(config)
    # coinciding_points_check()

    # hysplit_test.grid_test(False)  # full run
    # hysplit_test.grid_test(True)  # fast run
