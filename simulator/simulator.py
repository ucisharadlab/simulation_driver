import os

from model.param import Parameters


class Simulator:
    def __init__(self, params: [str]):
        self.params = params
        self.execution_params = dict()
        self.set_defaults()

    def get_defaults(self, params: dict = None) -> dict:
        pass

    def set_defaults(self, execution_params: dict = None):
        self.set_parameters(self.get_defaults())
        self.set_parameters(execution_params)

    def see_parameters(self) -> [str]:
        return self.params

    def get_parameter(self, name: str):
        return self.execution_params[name]

    def set_parameter(self, name: str, value) -> None:
        self.execution_params[name] = value

    def set_parameters(self, params: dict) -> None:
        if params is not None:
            self.execution_params.update(params)

    def preprocess(self) -> None:
        pass

    def specify_parameters(self, params: dict) -> None:
        self.set_parameters(params)

    def simulate(self) -> None:
        raise NotImplementedError()

    def postprocess(self) -> None:
        pass

    def run(self, params: dict = None) -> None:
        self.preprocess()
        if params is not None:
            self.specify_parameters(params)
        self.simulate()
        self.postprocess()

    def get_results(self) -> [dict]:
        raise NotImplementedError()


class CommandLineSimulator(Simulator):
    def simulate(self) -> None:
        command = self.prepare_command()
        print(f"Executing command: {command}")
        os.system(command)

    def prepare_command(self) -> str:
        raise NotImplementedError()

    def get_results(self) -> [dict]:
        raise NotImplementedError()


class NoopSimulator(CommandLineSimulator):
    def specify_parameters(self, params: dict) -> None:
        pass

    def prepare_command(self) -> str:
        return ""

    def get_results(self) -> [dict]:
        return [{"cell_id": 25, "fire_presence": 1}]


def get_simulator(name: str) -> Simulator:
    return NoopSimulator(["%param1%"])
