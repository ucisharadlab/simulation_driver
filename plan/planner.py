from plan.estimator import Estimator


class Planner:
    def __init__(self, estimator: Estimator):
        self.estimator = estimator

    def get_plan(self) -> [dict]:
        raise NotImplementedError()
