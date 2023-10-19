import json
import time
from datetime import datetime

import test
from plan.estimator import SimpleEstimator
from plan.planner import Planner, get_planner
from repo.edb_repo import EdbRepo
from simulator.hysplit import Hysplit
from simulator.simulator import NoopSimulator, Simulator

planners = dict()


def run(repo: EdbRepo, sleep: int = 2):
    while True:
        query_load = bundle(repo.get_query_load())
        set_planner('hysplit2', '"plan.planner.GreedyPlanner"',
                    repo.get_test_data('hysplit_test_data'))
        for learn_query in query_load["learn"]:
            _, simulator_name, planner_name, test_table = learn_query["query"].split(":")
            set_planner(simulator_name, planner_name, repo.get_test_data(test_table))
        for query in query_load["data"]:
            execution_info = dict()
            parsed_query = parse_query(query, repo)
            print(f"Query: {parsed_query['id']}, fetching relevant simulators")
            simulator_details = repo.get_simulators(parsed_query["output_type"])
            if len(simulator_details) <= 0:
                continue
            simulator_details = simulator_details[0]
            simulator_name = simulator_details["name"]
            print("Planning simulator input")
            previous_runs = repo.get_log(simulator_name)
            choice = planners[simulator_name].get_best_choice(previous_runs, parsed_query)
            if choice is None:
                continue
            params = json.loads(list(choice.keys())[0])
            simulator = get_simulator(simulator_name)
            print("Running simulation")
            start = datetime.now()
            simulator.run(params)
            execution_info["duration"] = (datetime.now() - start).total_seconds()
            print("Fetching and storing projected outputs")
            projections = simulator.get_results()
            repo.store_result(query["output_type"], projections)
            repo.log(simulator_name, params, execution_info)
        print("Finished cycle")
        time.sleep(sleep)


def set_planner(simulator_name: str, planner_name: str, test_data: dict = None) -> Planner:
    planner = get_planner(planner_name, SimpleEstimator())
    planner.learn(get_simulator(simulator_name), test_data)
    planners[simulator_name] = planner
    return planner


def bundle(query_load: [dict]) -> [dict]:
    bundled_queries = {"data": list(), "learn": list()}
    for query in query_load:
        if query["query"].lower().startswith("learn:"):
            bundled_queries["learn"].append(query)
            continue
        bundled_queries["data"].append(query)
    return bundled_queries


def parse_query(query: dict, repo: EdbRepo) -> dict:
    sql_query = (query["query"].replace("SELECT", "%%")
                 .replace("FROM", "%%")
                 .replace("WHERE", "%%"))
    _, select_query, from_query, where_query = sql_query.split("%%")
    columns = [column.strip() for column in select_query.split(',')]
    from_query = from_query.strip()

    result = None
    for column in columns:
        check_query = (f"SELECT column_name, type_key, data_type FROM simulated_columns "
                       f"WHERE table_name = '{from_query}' AND column_name = '{column}'")
        result = repo.fetch_entity(check_query)
        if result: break
    if not result: return query
    query["simulated_column"] = result[0]
    query["output_type"] = result[2]
    query["join_key"] = result[1]
    return query


def get_simulator(name: str) -> Simulator:
    if 'hysplit' in name.lower():
        return Hysplit(["%param1%"])
    return NoopSimulator(["%param1%"])
