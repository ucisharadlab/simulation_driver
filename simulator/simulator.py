class Simulator:
    def __init__(self, params: [str]):
        self.control_params = params
        self.execution_params = dict()

    def see_parameters(self) -> [str]:
        return self.control_params

    def set_parameter(self, key: str, value) -> None:
        self.execution_params[key] = value

    def set_parameters(self, params: dict) -> None:
        for key in params.keys():
            self.set_parameter(key, params[key])

    def run(self) -> None:
        pass

    def get_projection(self) -> dict:
        pass
