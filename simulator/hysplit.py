import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

import settings
from simulator.simulator import CommandLineSimulator
from util import strings, files


class Hysplit(CommandLineSimulator):
    def preprocess(self) -> None:
        self.set_path_params()

        os.chdir(self.get_working_path(f"."))
        for param in self.execution_params.keys():
            if param == "%keys_with_count%":
                continue
            old_value = self.execution_params[param]
            self.execution_params[param] = strings.macro_replace(self.execution_params, old_value)

    def postprocess(self) -> None:
        output_file = Path(self.get_parameter("%data_output%"))
        split_files_dir = output_file.parent
        data_file = split_files_dir.parent / (output_file.stem + ".txt")
        with data_file.open("w") as merged_data:
            merged_data.write(f"{data_file_schema}\n")
        for sample_file in split_files_dir.glob(output_file.stem + "_*"):
            sample_time = sample_file.stem.split("_")[-1]
            sample_hour, sample_minute = int(sample_time[0:2]), int(sample_time[-2:])
            with sample_file.open("r") as sample:
                sample_reader = csv.reader(sample, delimiter=',')
                headers = [value.strip() for value in next(sample_reader)]
                pollutant = headers[-1]
                for row in sample_reader:
                    line = [value.strip() for value in row]
                    timestamp = hysplit_data_start + timedelta(days=int(line[0]) - 1,
                                                               hours=sample_hour, minutes=sample_minute)
                    formatted_row = [timestamp.strftime("%Y-%m-%d %H:%M")] + line[2:-1] + [pollutant, line[-1]]
                    with data_file.open("a+") as merged_data:
                        writer = csv.writer(merged_data, delimiter=",", lineterminator='\n')
                        writer.writerow(formatted_row)
        self.set_parameter("%data_output%", str(data_file))
        os.chdir(self.execution_params["%original_path%"])

    def generate_config(self):
        control_params = self.get_parameter("%control_file%")[0]
        template_path = Path(self.get_parameter("%control_file%::%template_path%"))
        control_path = files.create_path_str(self.get_parameter("%control_file%::%path%"))

        files.generate_file(template_path / control_params["%template_file%"],
                            control_params["%name%"], str(control_path), self.execution_params)
        files.generate_file(template_path / control_params["%setup_template%"],
                            control_params["%setup_name%"], str(control_path), self.execution_params)
        files.copy(template_path / "ASCDATA.CFG", control_path / "ASCDATA.CFG")

    def prepare_command(self) -> [str]:
        self.setup_parameters()
        dump_path, output_file = self.setup_inputs()
        return [f"time {settings.HYSPLIT_PATH}/exec/hycs_std && echo 'Done simulation' && "
                f"time {settings.HYSPLIT_PATH}/exec/conappend -i{dump_path} -o{output_file} && echo 'Done append' && "
                f"time {settings.HYSPLIT_PATH}/exec/con2asc -i{output_file} -o{output_file} -t -x -u1.0E+9 -d "
                f"> /dev/null && echo 'Done conversion' "]

    def setup_parameters(self):
        for key in self.get_parameter("%keys_with_count%"):
            self.add_count(key)
        self.set_parameter("%output_grids%::%file%", strings.macro_replace(
            self.execution_params, self.get_parameter("%output_grids%::%file%")))
        self.generate_config()

    def setup_inputs(self) -> (Path, Path):
        filename = self.get_parameter('%output_grids%::%file%')
        output_dir = files.create_path_str(self.get_parameter("%output_grids%::%dir%")) / filename.replace("dump_", "")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"data_{filename}"
        dump_files = [str((grid['%dir%']) + "/" + grid['%file%']) for grid in self.get_parameter("%output_grids%")]
        dump_file_path = output_dir / f"dump_files_{get_date_suffix()}.txt"
        files.write_lines(dump_file_path, dump_files)
        self.set_parameter("%data_output%", str(output_file) + ".txt")
        return dump_file_path, output_file

    def get_results(self) -> [dict]:
        self.logger.info(f"Fetching results")
        filename = self.get_parameter("%data_output%")
        if Path(filename).stat().st_size == 0:
            return list()
        with open(filename) as file:
            lines = csv.reader(file, delimiter=",")
            header = [value.strip() for value in next(lines)]
            data = [{header[i]: line[i].strip() for i in range(0, len(header))}
                    for line in lines]
        for row in data:
            row["timestamp"] = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M")
        return data

    def add_count(self, key: str, count_key: str = None) -> None:
        if count_key is None:
            count_key = key[:-1] + "_count" + key[-1]
        self.set_parameter(count_key, str(len(self.get_parameter(key))))

    def set_path_params(self) -> None:
        working_path = self.get_working_path(f".")
        working_path.mkdir(parents=True, exist_ok=True)
        for param in self.get_parameter("%working_path_params%"):
            self.set_parameter(param, files.prefix_path(working_path, self.get_parameter(param)))
        absolute_path = self.get_absolute_path(f".")
        for param in self.get_parameter("%absolute_path_params%"):
            self.set_parameter(param, files.prefix_path(absolute_path, self.get_parameter(param)))

    def get_defaults(self, params: dict = None) -> dict:
        # TODO: Make relative paths relative to repo root
        return {
            "%name%": "test_helpers",
            "%start_locations%": ["34.12448, -118.40778"],
            # Edwards’ Point (https://losangelesexplorersguild.com/2021/03/16/center-of-los-angeles/)
            "%total_run_time%": str(7 * 24),
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
                "%span%": "1.0 1.0",
                "%dir%": f"./default/{datetime.now().strftime('%Y-%m-%d_%H-%M')}/",
                "%file%": "dump_%params%",
                "%vertical_level%": "1\n50",
                "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 00 30"
            }],
            "%timestep%": "30",
            "%deposition%": ["0.0 0.0 0.0\n0.0 0.0 0.0 0.0 0.0\n0.0 0.0 0.0\n0.0\n0.0"],
            "%control_file%": [{
                "%template_path%": "./debug/examples/hysplit",
                "%template_file%": "CONTROL_template",
                "%setup_template%": "SETUP_template",
                "%name%": "CONTROL",
                "%setup_name%": "SETUP.CFG",
                "%path%": "./"
            }],
            "%params%": "%name%_%start_locations_count%_%total_run_time%_%output_grids_count%_%pollutants_count%",
            "%working_path_params%": ["%output_grids%::%dir%", "%control_file%::%path%"],
            "%absolute_path_params%": ["%control_file%::%template_path%"],
            "%keys_with_count%": ["%start_locations%", "%input_data_grids%", "%output_grids%", "%pollutants%"]
        }


def get_sampling_rate_mins(sampling: str) -> int:
    sampling_param = sampling.split('\n')[-1].split(" ")
    hours = int(sampling_param[-2])
    minutes = int(sampling_param[-1])
    return 60 * hours + minutes


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


def get_date_suffix(date: datetime = datetime.now()) -> str:
    return date.strftime("%Y-%m-%d_%H-%M")


def get_param(name: str, value: str) -> tuple:
    name = name.replace("::", "%::%")
    return f"%{name}%", value


hysplit_data_start = datetime.strptime("1995-01-01", '%Y-%m-%d')
data_file_schema = "timestamp,latitude,longitude,pollutant,concentration"
