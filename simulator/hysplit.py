import csv
import os
import settings

from decimal import *
from datetime import datetime

from simulator.simulator import CommandLineSimulator
from util.util import FileUtil, StringUtil


class Hysplit(CommandLineSimulator):
    def preprocess(self) -> None:
        for param in self.execution_params.keys():
            if param == "%keys_with_count%":
                continue
            old_value = self.execution_params[param]
            self.execution_params[param] = StringUtil.macro_replace(self.execution_params, old_value)

    def generate_input(self):
        template_file = os.path.join(self.get_parameter("%control_file%")[0]["%template_path%"],
                                     self.get_parameter("%control_file%")[0]["%template_file%"])
        FileUtil.generate_file(template_file,
                               self.get_parameter("%control_file%")[0]["%name%"],
                               self.get_parameter("%control_file%")[0]["%path%"],
                               self.execution_params)

    def prepare_command(self) -> str:
        for key in self.get_parameter("%keys_with_count%"):
            self.add_count(key)
        self.generate_input()
        dump_files = list()
        output_grids = self.get_parameter("%output_grids%")
        output_dir = output_grids[0]['%dir%']
        for grid in output_grids:
            dump_files.append(os.path.join(grid['%dir%'], grid['%file%']))
        time_suffix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        dump_file_name = os.path.join(output_dir, f"dump_files_{time_suffix}.txt")
        with open(dump_file_name, 'w') as dump_file:
            dump_file.writelines(dump_files)
        output_file = os.path.join(output_dir, f"data_dump_{time_suffix}")
        self.set_parameter("%data_output%", dump_files[0] + ".txt")
        command = (f"time {settings.HYSPLIT_PATH}/exec/hycs_std && echo 'Done simulation' && "
                   # f"/Users/martin/Programming/simulation_hysplit/exec/conappend -i{dump_file_name} -o{output_file} && echo 'Done append' && "
                   f"time {settings.HYSPLIT_PATH}/exec/con2asc -i{dump_files[0]} -s -u1.0E+9 -d && echo 'Done conversion' ")
        return command

    def get_results(self) -> [dict]:
        filename = self.get_parameter("%data_output%")
        span = Decimal(self.get_parameter("%output_grids%")[0]["%spacing%"].split(" ")[0])
        data = list()
        with open(filename) as file:
            lines = csv.reader(file, delimiter=",")
            name = next(lines)[6]
            lines = [[value.strip() for value in line] for line in lines]
            data = [{"timestamp": f"{line[0]}-{line[1]}-{line[2]} {line[3]}:00",
                     "location": f"({Decimal(line[4]) - span / 2}, {Decimal(line[5]) - span / 2}), "
                                 f"({Decimal(line[4]) + span / 2}, {Decimal(line[5]) + span / 2})",
                     "name": name,
                     "concentration": line[6]} for line in lines]
        return data

    def add_count(self, key: str, count_key: str = None) -> None:
        if count_key is None:
            count_key = key[:-1] + "_count" + key[-1]
        self.set_parameter(count_key, str(len(self.get_parameter(key))))

    def get_defaults(self, params: dict = None) -> dict:
        return {
            "%name%": "test",
            "%start_locations%": ["34.12448, -118.40778"],  # Edwards’ Point (https://losangelesexplorersguild.com/2021/03/16/center-of-los-angeles/)
            "%total_run_time%": "240",
            "%input_data_grids%": [{
                    "%dir%": f"{settings.HYSPLIT_PATH}/working/",
                    "%file%": "oct1618.BIN"
                }
            ],
            "%pollutants%": [{
                "%id%": "AIR1",
                "%emission_rate%": "50.0",
                "%emission_duration_hours%": "144.0",
                "%release_start%": "00 00 00 00 00"
            }],
            "%output_grids%": [{
                "%centre%": "34.12448, -118.40778",
                "%spacing%": "0.05 0.05",
                "%span%": "0.5 0.5",
                "%dir%": f"./debug/hysplit_out/default/{datetime.now().strftime('%Y-%m-%d_%H-%M')}/",
                "%file%": "dump_default",
                "%vertical_level%": "1\n50",
                "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 00 30"
            }],
            "%deposition%": ["0.0 0.0 0.0\n0.0 0.0 0.0 0.0 0.0\n0.0 0.0 0.0\n0.0\n0.0"],
            "%params%": "%name%_%start_locations_count%_%total_run_time%_%output_grids_count%",
            "%control_file%": [{
                "%template_path%": "./debug/examples/hysplit",
                "%template_file%": "CONTROL_template",
                "%name%": "CONTROL",
                "%path%": "./"
            }],
            "%keys_with_count%": ["%start_locations%", "%input_data_grids%", "%output_grids%", "%pollutants%"]
        }
