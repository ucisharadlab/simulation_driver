import settings
from driver import Driver
from test import quality
from test.hysplit_test import *


def test_drive(sleep_seconds):
    repo = EdbRepo()
    simulation_driver = Driver(repo, sleep_seconds)
    simulation_driver.set_planner("hysplit", "plan.planner.GreedyPlanner",
                                  repo.get_test_data("hysplit_test_data"))
    simulation_driver.run()


if __name__ == '__main__':
    quality.measure_quality("%sampling%", "sampling", "2023-09-14 04:44")
    # test_drive(settings.DRIVER_SLEEP_SECONDS)
    # hysplit_test.coinciding_points_check()

    # hysplit_test.grid_test(False)  # full run
    # hysplit_test.grid_test(True)  # fast run
