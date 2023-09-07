import os

from simulator.simulator import CommandLineSimulator
from util.util import FileUtil, StringUtil


class Hysplit(CommandLineSimulator):
    def preprocess(self) -> None:
        for key in self.get_parameter("%keys_with_count%"):
            self.add_count(key)
        for param in self.execution_params.keys():
            if param == "%keys_with_count%":
                continue
            old_value = self.execution_params[param]
            self.execution_params[param] = StringUtil.macro_replace(self.execution_params, old_value)
        self.generate_input()

    def generate_input(self):
        template_file = os.path.join(self.get_parameter("%control_file%")[0]["%template_path%"],
                                     self.get_parameter("%control_file%")[0]["%template_file%"])
        FileUtil.generate_file(template_file,
                               self.get_parameter("%control_file%")[0]["%name%"],
                               self.get_parameter("%control_file%")[0]["%path%"],
                               self.execution_params)

    def prepare_command(self) -> str:
        command = "/Users/sriramrao/code/hysplit/hysplit/exec/hycs_std "
        for grid in self.get_parameter("%output_grids%"):
            output_path = os.path.join(grid['%dir%'], grid['%file%'])
            command += f"&& /Users/sriramrao/code/hysplit/hysplit/exec/concplot +g1 " \
                       f"-i{output_path} -c50 -j/Users/sriramrao/code/hysplit/hysplit/graphics/arlmap " \
                       f"-o{output_path}_plot.html"
        return command

    def get_results(self) -> [dict]:
        pass

    def add_count(self, key: str, count_key: str = None) -> None:
        if count_key is None:
            count_key = key[:-1] + "_count" + key[-1]
        self.set_parameter(count_key, str(len(self.get_parameter(key))))

    def get_defaults(self, params: dict = None) -> dict:
        return {
            "%name%": "test",
            "%start_locations%": ["35.727513, -118.786136"],
            "%total_run_time%": "240",
            "%input_data_grids%": [{
                    "%dir%": "/Users/sriramrao/code/hysplit/hysplit/working/",
                    "%file%": "oct1618.BIN"
                }
            ],
            "%pollutants%": [{
                "%id%": "AIR1",
                "%emission_rate%": "50.0",
                "%emission_duration_hours%": "96.0",
                "%release_start%": "00 00 00 00 00"
            }],
            "%output_grids%": [{
                "%centre%": "35.727513, -118.786136",
                "%spacing%": "0.1 0.1",
                "%span%": "10.0 10.0",
                "%dir%": "./",
                "%file%": "cdump_CA",
                "%vertical_level%": "1\n50",
                "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 01 00",
            }],
            "%deposition%": ["0.0 0.0 0.0\n0.0 0.0 0.0 0.0 0.0\n0.0 0.0 0.0\n0.0\n0.0"],
            "%params%": '%name%_%start_locations_count%_%total_run_time%_%output_grids_count%',
            "%control_file%": [{
                "%template_path%": '/Users/sriramrao/code/farsite/farsite_driver/examples/hysplit',
                "%template_file%": 'CONTROL_template',
                "%name%": "CONTROL",
                "%path%": "./"
            }],
            "%keys_with_count%": ["%start_locations%", "%input_data_grids%", "%output_grids%", "%pollutants%"]
        }
