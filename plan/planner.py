from plan.estimator import Estimator


class Planner:
    def __init__(self, estimator: Estimator):
        self.estimator = estimator

    def get_plan(self, query_load: list) -> [dict]:
        raise NotImplementedError()


class DummyPlanner(Planner):
    def get_plan(self, query_load: list) -> [dict]:
        parameter_choices = self.estimator.dump_model()
        ordered_parameters = list()
        epoch_minutes = query_load[0]["epoch"]
        for time in range(epoch_minutes, query_load[0]["duration_in_epochs"] * epoch_minutes + 1, epoch_minutes):
            filtered_parameters = {key: value for (key, value) in parameter_choices.items() if value[0] < time}
            ordered_parameters.append(max(filtered_parameters, key=lambda k: filtered_parameters[k][1]))
        return ordered_parameters
