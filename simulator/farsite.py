import geopandas as gpd
import os
from shapely.geometry import Point, Polygon

from simulator.simulator import CommandLineSimulator, Simulator
from util.util import FileUtil, StringUtil


def get_simulator(name: str) -> Simulator:
    return FarSite(["%space_file%", "%initial_fire_shape%", "%start_time%",
                    "%end_time%", "%timestep%", "%distance_res%", "%perimeter_res%"])


def check_distance(cell, surface):
    for polygon in surface:
        if cell.distance(polygon) <= 0.0:
            return 1
    return 0


def get_fire_mapping(surface, points_grid, save_path):
    row = ''
    for row in points_grid:
        for cell in row:
            row += str(check_distance(cell, surface)) + ','
        row += '\n'
    with open(save_path, 'w') as mapping_file:
        mapping_file.write(row)

    return 0


def get_points_grid(coordinates: tuple, unit: int):
    points_grid = list()
    x_min, y_min, x_max, y_max = coordinates[0][0], coordinates[0][1], \
                                 coordinates[1][0], coordinates[1][1]
    for y in range(y_min + unit, y_max + unit, unit):
        row = list()
        for x in range(x_min + unit, x_max + unit, unit):
            row.append(Point(x - unit / 2, y - unit / 2))
        points_grid.append(row)
    return points_grid


def generate_poly_dict(perimeters):
    poly_dict = dict()
    Month, Day, Hour = 5, 4, 2  # i[1], i[2], i[3]
    time_instance = int((Day - 4) * 24 * 60 + (Hour // 100) * 60 + (Hour % 100))
    if time_instance not in poly_dict:
        poly_dict[time_instance] = list()
    poly_dict[time_instance].append(Polygon(perimeters))
    return poly_dict


def generate_cell_mapping(perimeters_file: str, target_path: str, coordinates: tuple, unit: int) -> None:
    df1 = gpd.read_file(perimeters_file)
    poly_dict = generate_poly_dict(df1)
    points_set = get_points_grid(coordinates, unit)
    x_num = (coordinates[0][0] - coordinates[1][0]) // unit + 1
    for time_instance in poly_dict:
        surface = poly_dict[time_instance]
        save_filename = str(time_instance) + '.csv'
        save_filepath = os.path.join(target_path, save_filename)
        get_fire_mapping(surface, points_set, save_filepath)


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
        generate_cell_mapping(self.get_parameter("%fire_perimeters_file%"),
                              self.get_parameter("%cell_mappings_path%"),
                              self.get_parameter("%coordinates%"),
                              self.get_parameter("%unit%"))

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
