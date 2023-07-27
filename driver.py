from plan.planner import Planner
from repo.edb_repo import EdbRepo
from simulator.farsite import get_simulator


def run(repo: EdbRepo, planner: Planner, query_load: [dict]):
    for query in query_load:
        simulators = repo.get_simulators(query["output_type"])
        params = planner.get_best_choice(query, simulators)
        simulator = get_simulator(params["simulator"])
        simulator.run(params)
        projections = simulator.get_results()
        repo.store_result(projections, query["simulation_name"])
