from simulator.simulator import Simulator


class Estimator:
    # Constructor
    def __init__(self, name: str):
        pass

    # For any initial setup
    def setup(self):
        pass

    # To learn estimation model
    # Inputs: processor instance to learn the model for
    #         test inputs to learn the model (optional)
    def learn(self, processor: Simulator, test_inputs: [dict] = None) -> None:
        raise NotImplementedError()

    # To estimate (cost, quality) for a given set of inputs
    def estimate(self, inputs: dict) -> tuple:
        raise NotImplementedError()
