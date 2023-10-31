from driver import Driver
import settings
from repo.edb_repo import EdbRepo
from test import hysplit_test
from test.driver_test import driver_data_queries_test


def test_drive(sleep_seconds):
    repo = EdbRepo()
    simulation_driver = Driver(repo, sleep_seconds)
    simulation_driver.set_planner("hysplit", "plan.planner.GreedyPlanner",
                                  repo.get_test_data("hysplit_test_data"))
    simulation_driver.run()


if __name__ == '__main__':
    test_drive(settings.DRIVER_SLEEP_SECONDS)
    # hysplit_test.coinciding_points_check()

    # hysplit_test.grid_test(False)  # full run
    # hysplit_test.grid_test(True)  # fast run
