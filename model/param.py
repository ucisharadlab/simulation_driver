class Parameters:
    def __init__(self, parameters=None):
        if parameters is None:
            parameters = dict()
        self.parameters = parameters

    def get_parameters(self) -> [str]:
        return self.parameters.keys()

    def get_value(self, parameter_name: str):
        return self.parameters.get(parameter_name)

    def set_value(self, parameter_name: str, value) -> None:
        self.parameters[parameter_name] = value

    def set_values(self, params: dict) -> None:
        for key in params.keys():
            self.set_value(key, params[key])

    def __eq__(self, other):
        return self.parameters == other.parameters
