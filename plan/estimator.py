class Estimator:
    def setup(self):
        raise NotImplementedError()

    def learn(self):
        raise NotImplementedError()

    def estimate(self):
        raise NotImplementedError()
