import os

from simulator.simulator import CommandLineSimulator
from util import FileUtil, StringUtil


class FarSite(CommandLineSimulator):
    def preprocess(self) -> None:
        self.generate_input_files()

    def prepare_command(self) -> str:
        return f'{self.get_parameter("%base_path%")}/src/TestFARSITE {self.get_parameter("%run_file%")} 2>&1 '

    def get_results(self) -> [dict]:
        pass

    def generate_input_files(self) -> str:
        # TODO: Refactor
        self.set_parameter("%input_file_name%", FileUtil.generate_file(
            self.get_parameter("%input_file_template%"),
            self.get_parameter("%input_file_name_template%"),
            self.get_parameter("%input_file%"),
            self.execution_params))
        self.set_parameter("%output_path%", self.create_output_path())
        return FileUtil.generate_file(
            self.get_parameter("%run_file_template%"),
            self.get_parameter("%run_file_name_template%"),
            self.get_parameter("%run_file%"),
            self.execution_params)

    def create_output_path(self) -> str:
        output_path = self.get_parameter("%preset_output_path%")
        output_path = FileUtil.sanitise_filename(StringUtil.macro_replace(self.execution_params, output_path))
        FileUtil.create_path(output_path)
        return output_path
