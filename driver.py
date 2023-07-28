from plan.planner import Planner
from repo.edb_repo import EdbRepo
from simulator.simulator import get_simulator


def run(repo: EdbRepo, planner: Planner, query_load: [dict]):
    for query in query_load:
        print(f"Query: {query['name']}, fetching relevant simulators")
        simulators = repo.get_simulators(query["output_type"])
        print("Planning simulator input")
        params = planner.get_best_choice(query, simulators)
        simulator = get_simulator("params['simulator']")
        print("Running simulation")
        simulator.run(params)
        print("Fetching and storing projected outputs")
        projections = simulator.get_results()
        repo.store_result(query["simulation_name"], projections)
