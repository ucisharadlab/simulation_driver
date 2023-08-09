import test
from plan.estimator import DummyEstimator
from plan.planner import Planner, GreedyPlanner
from repo.edb_repo import EdbRepo
from simulator.simulator import get_simulator, NoopSimulator


def run(repo: EdbRepo):
    query_load = bundle(repo.get_query_load())
    for query in query_load:
        print(f"Query: {query['name']}, fetching relevant simulators")
        simulators = repo.get_simulators(query["output_type"])
        planner = get_planner(query["output_type"])
        print("Planning simulator input")
        params = planner.get_best_choice(query, simulators)
        simulator = get_simulator(f"{params['simulator']}")
        print("Running simulation")
        simulator.run(params)
        print("Fetching and storing projected outputs")
        projections = simulator.get_results()
        repo.store_result(query["simulation_name"], projections)


def get_planner(output_type: str) -> Planner:
    estimator = DummyEstimator("test")
    estimator.learn(NoopSimulator(""), test.get_data())
    planner = GreedyPlanner(estimator)
    return planner


def bundle(query_load: [dict]) -> [dict]:
    return query_load
