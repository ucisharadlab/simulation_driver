import os

from model.param import Parameters


class Simulator:
    def __init__(self, params: [str]):
        self.params = params
        self.execution_params = Parameters()

    def see_parameters(self) -> [str]:
        return self.params

    def get_parameter(self, name: str):
        return self.execution_params.get_value(name)

    def set_parameter(self, name: str, value) -> None:
        self.execution_params.set_value(name, value)

    def set_parameters(self, params: dict) -> None:
        self.execution_params.set_values(params)

    def preprocess(self) -> None:
        pass

    def specify_parameters(self, params: dict) -> None:
        self.set_parameters(params)

    def simulate(self) -> None:
        raise NotImplementedError()

    def postprocess(self) -> None:
        pass

    def run(self, params: dict) -> None:
        self.preprocess()
        self.specify_parameters(params)
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
