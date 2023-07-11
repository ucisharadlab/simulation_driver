import os

from simulator.simulator import CommandLineSimulator
from util.util import FileUtil, StringUtil


class FarSite(CommandLineSimulator):
    def preprocess(self) -> None:
        self.set_parameters({
            "%start_time%": "05 04 0000",
            "%end_time%": "05 04 0500",
            "%timestep%": "5",
            "%distance_res%": "5",
            "%perimeter_res%": "5",
            "%params%": '%timestep%_%distance_res%_%perimeter_res%_%start_time%_%end_time%',
            "%base_path%": '/Users/sriramrao/code/farsite/farsite_driver',
            "%space_file%": "examples/FQ_burn/input/Burn.lcp",
            "%initial_fire_shape%": "examples/FQ_burn/input/FQ_burn.shp",
            "%run_file_path%": 'examples/FQ_burn/run_file',
            "%run_file_template%": 'runBurn_template.txt',
            "%run_file_name_template%": "runBurn_%params%.txt",
            "%input_file_path%": 'examples/FQ_burn/Burn_inputfiles',
            "%input_file_template%": 'burn_template.input',
            "%input_file_name_template%": 'burn_%params%.input',
            "%output_path%": "%base_path%/examples/FQ_burn/output/burn_%params%/"
        })
        for param in self.execution_params.keys():
            old_value = self.execution_params[param]
            self.execution_params[param] = StringUtil.macro_replace(self.execution_params, old_value)
        self.generate_input_files()

    def prepare_command(self) -> str:
        return f'{self.get_parameter("%base_path%")}/src/TestFARSITE {self.get_parameter("%run_file%")} 2>&1 '

    def get_results(self) -> [dict]:
        pass

    def generate_input_files(self) -> str:
        # TODO: Refactor to remove execution params from method call
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
