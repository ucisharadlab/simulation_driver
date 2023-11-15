from model.param import Parameters
from simulator.simulator import Simulator


class Estimator:
    # Constructor
    def __init__(self):
        pass

    # For any initial setup
    def setup(self):
        pass

    # To learn estimation model
    # Inputs: processor instance to learn the model for
    #         test_helpers data set to learn the model (optional)
    def learn(self, processor: Simulator, test_data: dict = None) -> None:
        raise NotImplementedError()

    # To estimate (cost, quality) for a given set of inputs
    def estimate(self, inputs: dict) -> tuple:
        raise NotImplementedError()

    def dump_model(self):
        raise NotImplementedError()


class SimpleEstimator(Estimator):
    def __init__(self):
        super().__init__()
        self.estimates = dict()

    def learn(self, processor: Simulator, test_data: dict = None) -> None:
        self.estimates = test_data

    def estimate(self, inputs: dict) -> Parameters:
        if self.estimates is None or inputs not in self.estimates.keys():
            return Parameters()
        return self.estimates.get(inputs)

    def dump_model(self):
        return self.estimates
