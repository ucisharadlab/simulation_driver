import os


class Simulator:
    def __init__(self, params: [str]):
        self.params = params
        self.execution_params = dict()

    def see_parameters(self) -> [str]:
        return self.params

    def get_parameter(self, key: str):
        return self.execution_params[key]

    def set_parameter(self, key: str, value) -> None:
        self.execution_params[key] = value

    def set_parameters(self, params: dict) -> None:
        for key in params.keys():
            self.set_parameter(key, params[key])

    def preprocess(self) -> None:
        pass

    def simulate(self) -> None:
        raise NotImplementedError()

    def postprocess(self) -> None:
        pass

    def run(self) -> None:
        self.preprocess()
        self.simulate()
        self.postprocess()

    def get_results(self) -> [dict]:
        raise NotImplementedError()


class CommandLineSimulator(Simulator):
    def simulate(self) -> None:
        print("Executing command")
        os.system(self.prepare_command())

    def prepare_command(self) -> str:
        raise NotImplementedError()

    def get_results(self) -> [dict]:
        raise NotImplementedError()
