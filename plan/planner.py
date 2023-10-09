import json

from plan.estimator import Estimator
from simulator.simulator import Simulator


class Planner:
    def __init__(self, estimator: Estimator):
        self.estimator = estimator

    def learn(self, processor: Simulator, test_data: dict) -> None:
        self.estimator.learn(processor, test_data)

    def get_plan(self, log: list, query_load: list) -> [dict]:
        raise NotImplementedError()

    def get_best_choice(self, log: list, query: dict) -> dict:
        plan = self.get_plan(log, [query])
        return plan[0] if len(plan) > 0 else None


class GreedyPlanner(Planner):
    def get_plan(self, log: list, query_load: list) -> [dict]:
        parameter_choices = self.estimator.dump_model()
        ordered_parameters = sorted(parameter_choices.items(), key=lambda e: e[1]["cost"])
        previous_params = [entry["params"] for entry in log]
        available_params = list()
        for param, cost in ordered_parameters:
            if json.loads(param) not in previous_params:
                available_params.append({param: cost})
        # ordered_parameters = [param for param in ordered_parameters if param not in previous_params]
        return available_params


def get_planner(name: str, estimator: Estimator) -> Planner:
    return GreedyPlanner(estimator)
