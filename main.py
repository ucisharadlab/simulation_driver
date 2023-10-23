import driver
import settings
from repo.edb_repo import EdbRepo


def test_drive(sleep_seconds):
    db_repo = EdbRepo()
    simulation_driver = driver.Driver(db_repo, sleep_seconds)
    simulation_driver.run()


if __name__ == '__main__':
    test_drive(settings.DRIVER_SLEEP_SECONDS)
    # hysplit_test.coinciding_points_check()

    # hysplit_test.grid_test(False)  # full run
    # hysplit_test.grid_test(True)  # fast run
