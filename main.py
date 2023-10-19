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


if __name__ == '__main__':
    test_drive()
    # hysplit_test.coinciding_points_check()

    # hysplit_test.grid_test(False)  # full run
    # hysplit_test.grid_test(True)  # fast run
