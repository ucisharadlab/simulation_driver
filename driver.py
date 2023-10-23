import json
import time
from datetime import datetime

from plan.planner import Planner, get_planner
from repo.edb_repo import EdbRepo
from simulator.simulator import Simulator, get_simulator
from util import reflection_util


class Driver:
    def __init__(self, simulator_repo, sleep_seconds: int = 0):
        self.repo = simulator_repo
        self.planners = dict()
        self.threads = dict()
        self.sleep_seconds = sleep_seconds

    def run(self):
        while True:
            query_load = bundle(self.repo.get_query_load())
            for learn_query in query_load["learn"]:
                _, simulator_name, planner_name, test_table = learn_query["query"].split(":")
                self.set_planner(simulator_name, planner_name, self.repo.get_test_data(test_table))
            for query in query_load["data"]:
                parsed_query = parse_query(query, self.repo)
                simulator_details = self.repo.get_simulator(query["output_type"])
                if len(simulator_details.keys()) <= 0:
                    continue
                simulator_name = simulator_details["name"]
                execution_info = self.plan_and_simulate(parsed_query, simulator_name)
                self.repo.log(simulator_name, execution_info)
            print("Finished cycle")
            time.sleep(self.sleep_seconds)

    def plan_and_simulate(self, query: dict, simulator_name: str):
        print(f"Query: {query['id']}, beginning plan and simulate")
        print("Planning simulator input")
        previous_runs = self.repo.get_log(simulator_name)
        choice = self.planners[simulator_name].get_best_choice(previous_runs, query)
        if choice is None:
            return dict()

        execution_info = dict()
        execution_info["params"] = json.loads(list(choice.keys())[0])
        simulator = get_simulator(simulator_name)
        print("Running simulation")
        start = datetime.now()
        simulator.run(execution_info["params"])
        execution_info["duration"] = (datetime.now() - start).total_seconds()
        results = simulator.get_results()

        print("Storing projected outputs")
        self.repo.store_result(query["output_type"], results)
        return execution_info

    def set_planner(self, simulator_name: str, planner_name: str, test_data: dict = None) -> Planner:
        planner = get_planner(planner_name)
        planner.learn(get_simulator(simulator_name), test_data)
        self.planners[simulator_name] = planner
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
