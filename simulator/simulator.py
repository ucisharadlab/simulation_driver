import logging
from multiprocessing import current_process
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT

from util import reflection


class Simulator:
    def __init__(self, params: dict = None):
        self.execution_params = dict()
        self.set_defaults(params)
        self.logger = logging.getLogger()
        self.set_parameter(original_dir_macro, str(Path().resolve()))
        self.set_parameter(base_dir_macro, str(Path(f"./debug/hysplit_out/{current_process().name}").resolve()))

    def get_defaults(self, params: dict = None) -> dict:
        pass

    def set_defaults(self, execution_params: dict = None):
        self.set_parameters(self.get_defaults())
        self.set_parameters(execution_params)

    def get_parameter(self, name: str):
        if "::" not in name:
            return self.execution_params[name]
        outer_key, inner_key = get_split_keys(name)
        if (outer_key not in self.execution_params
                or len(self.execution_params[outer_key]) == 0
                or inner_key not in self.execution_params[outer_key][0]):
            return None
        return self.execution_params[outer_key][0][inner_key]

    def set_parameter(self, name: str, value) -> None:
        if "::" not in name:
            self.execution_params[name] = value
            return
        outer_key, inner_key = get_split_keys(name)
        if outer_key not in self.execution_params:
            self.execution_params[outer_key] = [dict()]
        self.execution_params[outer_key][0][inner_key] = value

    def set_parameters(self, params: dict) -> None:
        if not params:
            return
        for key in params.keys():
            self.set_parameter(key, params[key])

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

    def get_working_path(self, relative_path: str):
        return Path(self.execution_params[base_dir_macro]).resolve() / relative_path

    def get_absolute_path(self, relative_path: str):
        return Path(self.execution_params[original_dir_macro]).resolve() / relative_path


class CommandLineSimulator(Simulator):
    def simulate(self) -> None:
        commands = self.prepare_command()
        for command in commands:
            self.logger.info(f"In directory: {Path().resolve()}, executing command: {command}")
            process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True)
            with process.stdout:
                for line in iter(process.stdout.readline, b''):
                    if not line:
                        break
                    self.logger.info(line.rstrip())
            process.wait()
        self.logger.info("Completed execution")

    def prepare_command(self) -> [str]:
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


def get_simulator(full_class_name: str) -> Simulator:
    return reflection.get_instance(full_class_name)


def get_split_keys(composite_key: str) -> (str, str):
    assert composite_key.count("::") == 1
    outer_key = composite_key[:composite_key.find("::")]
    inner_key = composite_key[composite_key.find("::") + 2:]
    return outer_key, inner_key


base_dir_macro = "%base_working_dir%"
original_dir_macro = "%original_path%"
