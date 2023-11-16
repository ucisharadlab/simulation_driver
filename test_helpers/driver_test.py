import settings
from driver import Driver
from repo.edb_repo import EdbRepo, prepare_test_data_row
from test_helpers.test_data import *


def driver_data_queries_test():
    driver = Driver(EdbRepo(), settings.DRIVER_SLEEP_SECONDS)
    driver.set_planner("hysplit",
                       "plan.planner.GreedyPlanner",
                       get_test_planner_data())
    driver.handle_data_queries(data_queries)

    while 0 < driver.check_simulation_statuses():
        pass

    print("Threads complete")


# if __name__ == '__main__':
#     driver_data_queries_test()
