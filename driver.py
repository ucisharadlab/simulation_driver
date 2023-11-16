import json
import threading
import time
from datetime import datetime

from plan.planner import Planner, get_planner
from repo.edb_repo import EdbRepo
from simulator.simulator import get_simulator


class Driver:
    def __init__(self, simulator_repo: EdbRepo, sleep_seconds: int = 0):
        self.repo = simulator_repo
        self.planners = dict()
        self.runtimes = list()
        self.sleep_seconds = sleep_seconds

    def run(self):
        while True:
            query_load = bundle(self.repo.get_query_load())
            print(f"Initiating learn steps")
            self.handle_learn_queries(query_load["learn"])
            self.handle_data_queries(query_load["data"])
            print(f"Checking ongoing simulation statuses")
            self.check_simulation_statuses()
            print("Finished cycle")
            time.sleep(self.sleep_seconds)

    def handle_learn_queries(self, learn_queries: list):
        for query in learn_queries:
            _, simulator_name, planner_name, test_table = query["query"].split(":")
            self.set_planner(simulator_name, planner_name, self.repo.get_test_data(test_table))

    def handle_data_queries(self, data_queries: list):
        for query in data_queries:
            print(f"Query: {query['id']}, setting up execution")
            parsed_query = parse_query(query, self.repo)
            simulator_details = self.repo.get_simulator_by_type(parsed_query["output_type"])
            if len(simulator_details.keys()) <= 0:
                continue
            simulator_name = simulator_details["name"]
            plan = self.planners[simulator_name].get_plan(self.repo.get_log(simulator_name), parsed_query)
            for params, cost in plan:
                self.execute_runtime(parsed_query, simulator_details["class_name"], params)

            # TODO: Join is here only because thread.is_alive() doesn't seem to work
            for runtime in self.runtimes:
                runtime.join()

    def check_simulation_statuses(self) -> int:
        print(f"Running threads: {len(self.runtimes)}")
        completed_ids = list()
        for runtime in self.runtimes:
            if runtime.is_alive():
                continue
            runtime.handled = True
            completed_ids.append(runtime.query_id)

        self.runtimes = [r for r in self.runtimes if not r.handled]
        self.repo.complete_queries(completed_ids)
        return len(self.runtimes)

    def execute_runtime(self, query: dict, simulator_class: str, params: str):
        runtime = threading.Thread(target=self.run_simulation,
                                   args=(query, simulator_class, params))
        self.runtimes.append(runtime)
        runtime.handled = False
        runtime.name = f"runtime-{len(self.runtimes)}"
        runtime.query_id = query['id']
        runtime.start()

    def run_simulation(self, query: dict, simulator_name: str, params: str):
        execution_info = dict()
        execution_info["params"] = json.loads(params, strict=False)
        simulator = get_simulator(simulator_name)

        print("Running simulation")
        start = datetime.now()
        simulator.run(execution_info["params"])
        results = simulator.get_results()

        print("Storing projected outputs and logs")
        self.repo.store_result(query["output_type"], results)
        execution_info["duration"] = (datetime.now() - start).total_seconds()
        self.repo.log(simulator_name, execution_info)

    def set_planner(self, simulator_name: str, planner_name: str, test_data: dict = None) -> Planner:
        planner = get_planner(planner_name)
        simulator = self.repo.get_simulator_by_name(simulator_name)
        planner.learn(get_simulator(simulator["class_name"]), test_data)
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
        if result:
            break
    if not result:
        return query
    query["simulated_column"] = result[0]
    query["output_type"] = result[2]
    query["join_key"] = result[1]
    return query
