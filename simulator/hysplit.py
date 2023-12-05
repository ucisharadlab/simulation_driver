import csv
import os
import shutil
from datetime import datetime
from pathlib import Path

import settings
from simulator.simulator import CommandLineSimulator, base_dir_macro
from util import strings


class Hysplit(CommandLineSimulator):
    def preprocess(self) -> None:
        working_path = self.get_absolute_path(self.get_parameter(base_dir_macro))
        working_path.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.get_absolute_path("./ASCDATA.CFG"), working_path / "ASCDATA.CFG")
        output_dir = self.get_parameter("%output_grids%::%dir%")
        self.set_parameter("%output_grids%::%dir%", str(working_path / output_dir) + "/")
        os.chdir(working_path)
        for param in self.execution_params.keys():
            if param == "%keys_with_count%":
                continue
            old_value = self.execution_params[param]
            self.execution_params[param] = strings.macro_replace(self.execution_params, old_value)

    def postprocess(self) -> None:
        os.chdir(self.execution_params[base_dir_macro])

    def generate_input(self):
        control_params = self.get_parameter("%control_file%")[0]
        template_file = (self.get_absolute_path(control_params["%template_path%"])
                         / control_params["%template_file%"])
        file.generate_file(template_file, control_params["%name%"], control_params["%path%"], self.execution_params)

    def prepare_command(self) -> [str]:
        for key in self.get_parameter("%keys_with_count%"):
            self.add_count(key)
        self.set_parameter("%output_grids%::%file%", strings.macro_replace(
            self.execution_params, self.execution_params["%output_grids%"][0]["%file%"]))

        output_grids = self.get_parameter("%output_grids%")
        output_dir = self.get_absolute_path(output_grids[0]['%dir%'])
        output_dir.mkdir(parents=True, exist_ok=True)
        self.generate_input()
        dump_files = list()
        for grid in output_grids:
            dump_files.append(str(self.get_absolute_path(grid['%dir%']) / grid['%file%']) + "\n")
        time_suffix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        dump_file_name = output_dir / f"dump_files_{time_suffix}.txt"
        with open(dump_file_name, 'w') as dump_file:
            dump_file.writelines(dump_files)
        file_suffix = output_grids[0]["%file%"]
        output_file = output_dir / f"data_{file_suffix}"
        self.set_parameter("%data_output%", dump_files[0] + ".txt")
        commands = [f"time {settings.HYSPLIT_PATH}/exec/hycs_std && echo 'Done simulation' && "
                    f"time {settings.HYSPLIT_PATH}/exec/conappend -i{dump_file_name} -o{output_file} && echo 'Done append' && "
                    f"time {settings.HYSPLIT_PATH}/exec/con2asc -i{output_file} -s -u1.0E+9 -d && echo 'Done conversion' "]
        return commands

    def get_results(self) -> [dict]:
        self.logger.info(f"Fetching results")
        filename = self.get_parameter("%data_output%")
        sampling_rate = get_sampling_rate_mins(self.get_parameter("%output_grids%::%sampling%"))
        if Path(filename).stat().st_size == 0:
            return list()
        with open(filename) as file:
            lines = csv.reader(file, delimiter=",")
            header = next(lines)
            pollutant_name = header[6]
            data = list()
            previous_row = dict()
            match_count = 0
            for raw_line in lines:
                line = [value.strip() for value in raw_line]
                new_timestamp = line_timestamp = f"{line[0]}-{line[1]}-{line[2]} {line[3]}:00"
                row = {"latitude": f"{line[4]}",
                       "longitude": f"{line[5]}",
                       "name": pollutant_name,
                       "concentration": line[6]}
                if len(previous_row) == 0 or not check_row_dimensions(previous_row, row):
                    match_count = 0
                elif sampling_rate < 60:
                    match_count += 1
                    new_timestamp = new_timestamp.replace(":00",
                                                          f":{((match_count * sampling_rate) % 60):02}")
                previous_row = row.copy()
                row["timestamp"] = get_time(new_timestamp if new_timestamp != line_timestamp else line_timestamp)
                data.append(row)
        return data

    def add_count(self, key: str, count_key: str = None) -> None:
        if count_key is None:
            count_key = key[:-1] + "_count" + key[-1]
        self.set_parameter(count_key, str(len(self.get_parameter(key))))

    def get_defaults(self, params: dict = None) -> dict:
        # TODO: Make relative paths relative to repo root
        return {
            "%name%": "test_helpers",
            "%start_locations%": ["34.12448, -118.40778"],
            # Edwards’ Point (https://losangelesexplorersguild.com/2021/03/16/center-of-los-angeles/)
            "%total_run_time%": "240",
            "%input_data_grids%": [{
                "%dir%": f"{settings.HYSPLIT_PATH}/working/",
                "%file%": "oct1618.BIN"
            }],
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
                "%dir%": f"./default/{datetime.now().strftime('%Y-%m-%d_%H-%M')}/",
                "%file%": "dump_%params%",
                "%vertical_level%": "1\n50",
                "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 00 30"
            }],
            "%deposition%": ["0.0 0.0 0.0\n0.0 0.0 0.0 0.0 0.0\n0.0 0.0 0.0\n0.0\n0.0"],
            "%params%": "%name%_%start_locations_count%_%total_run_time%_%output_grids_count%_%pollutants_count%",
            "%control_file%": [{
                "%template_path%": "./debug/examples/hysplit",
                "%template_file%": "CONTROL_template",
                "%name%": "CONTROL",
                "%path%": "./"
            }],
            "%keys_with_count%": ["%start_locations%", "%input_data_grids%", "%output_grids%", "%pollutants%"]
        }


def get_sampling_rate_mins(sampling: str) -> int:
    sampling_param = sampling.split('\n')[-1].split(" ")
    days = int(sampling_param[0]) if len(sampling_param) == 3 else 0
    hours = int(sampling_param[-2])
    minutes = int(sampling_param[-1])
    return 24 * 60 * int(days) + 60 * int(hours) + int(minutes)


def check_row_dimensions(row1: dict, row2: dict) -> bool:
    row1_dims = remove_metrics(row1)
    row2_dims = remove_metrics(row2)
    return row1_dims == row2_dims


def remove_metrics(row: dict) -> dict:
    row_dims = row.copy()
    row_dims["concentration"] = ""
    return row_dims


def get_time(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M")


def get_date_path_suffix(date_str: str) -> str:
    return get_date_suffix(get_time(date_str))


def get_date_suffix(date: datetime) -> str:
    return date.strftime("%Y-%m-%d_%H-%M")


def get_param(name: str, value: str) -> tuple:
    return f"%{name}%", value
