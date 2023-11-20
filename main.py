import logging

import settings
from driver import Driver
from measures import quality
from repo.edb_repo import EdbRepo
from test_helpers.hysplit_test import *


def init():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
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
    quality_check()
    # coinciding_points_check()

    # hysplit_test.grid_test(False)  # full run
    # hysplit_test.grid_test(True)  # fast run
