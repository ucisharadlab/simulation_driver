import json

from simulator.simulator import Simulator
from util import reflection


class Planner:
    def __init__(self):
        self.estimator = None
        self.set_estimator("plan.estimator.SimpleEstimator")

    def set_estimator(self, estimator_name):
        self.estimator = reflection.get_instance(estimator_name)

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
        ordered_parameters = sorted(parameter_choices.items(), key=lambda e: e[1]["cost"], reverse=True)
        previous_params = [entry["params"] for entry in log]
        chosen_params = self.choose_parameters(ordered_parameters)

        plan = list()
        for param, cost in chosen_params:
            if json.loads(param, strict=False) not in previous_params:
                plan.append((param, cost))
        return plan

    def choose_parameters(self, ordered_parameters: list):
        plan = list()
        params_count = len(ordered_parameters)
        if params_count == 0:
            return plan
        plan.append(ordered_parameters[0])
        if params_count == 2:
            plan.append(ordered_parameters[1])
            return plan
        # plan.append(ordered_parameters[-2])
        plan.insert(0, ordered_parameters[-1])
        return plan


def get_planner(name: str) -> Planner:
    return reflection.get_instance(name)
