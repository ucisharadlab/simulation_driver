import os

from cell_mappings import generate_cell_mapping
from repo.sql_repo import SqlRepo

base_path = '/Users/sriramrao/code/farsite/farsite_driver'
run_file_path = 'examples/FQ_burn/run_file'
run_file_template = 'runBurn_template.txt'
run_file_name_template = 'runBurn_%params%.txt'
input_file_path = 'examples/FQ_burn/Burn_inputfiles'
input_file_template = 'burn_template.input'
input_file_name_template = 'burn_%params%.input'
params = '%timestep%_%distance_res%_%perimeter_res%_%start_time%_%end_time%'
input_parameters = {
    (120, 5, 5, 5): (3, 0.7),
    (120, 10, 5, 5): (1.5, 0.6),
    (120, 8, 10, 10): (0.5, 0.55),
}
x_min, y_min, x_max, y_max = 702200.0, 4309600.0, 702900.0, 4310200.0
unit = 10
repo = SqlRepo()


def create_output_path(settings: dict) -> str:
    output_path = settings["%preset_output_path%"]
    output_path = sanitise_file_name(macro_replace(settings, output_path))
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    print(output_path)
    return output_path


def sanitise_file_name(name: str) -> str:
    filename, extension = os.path.splitext(name)
    return filename.replace(" ", "_").replace(".", "_") + extension


def execute_simulator(run_file: str):
    cmd = f'{base_path}/src/TestFARSITE {run_file} 2>&1 '
    print(cmd)
    # os.system(cmd)
    print(f"Finished simulating for {run_file}")


def init(settings: dict):
    settings["%base_path%"] = base_path
    settings["%run_file_path%"] = run_file_path
    settings["%run_file_template%"] = run_file_template
    settings["%input_file_path%"] = input_file_path
    settings["%input_file_template%"] = input_file_template
    settings["%preset_output_path%"] = f"%base_path%/examples/FQ_burn/output/burn_%params%/"


def add_execution_params(settings: dict):
    settings["%space_dir%"] = "examples/FQ_burn/input"
    settings["%space_file%"] = "Burn.lcp"
    settings["%initial_fire_shape%"] = "FQ_burn.shp"
    settings["%start_time%"] = "05 04 0000"
    settings["%end_time%"] = "05 04 0200"
    settings["%timestep%"] = "1"
    settings["%distance_res%"] = "5"
    settings["%perimeter_res%"] = "5"
    settings["%params%"] = macro_replace(settings, params)


def run_experiment_te(settings: dict):
    settings["%space_dir%"] = "examples/FQ_burn/input"
    settings["%space_file%"] = "Burn.lcp"
    settings["%initial_fire_shape%"] = "FQ_burn.shp"
    settings["%start_time%"] = "05 04 0000"
    # settings["%end_time%"] = "05 04 0200"
    settings["%timestep%"] = "5"
    settings["%distance_res%"] = "5.0"
    settings["%perimeter_res%"] = "5.0"
    settings["%params%"] = macro_replace(settings, params)
    # starting with temporal extent
    for i in range(0, 515, 15):
        settings["%end_time%"] = f"05 04 {i:04d}"
        execute_simulator(generate_input_files(settings))


def run_experiment_ts(settings: dict):
    settings["%space_dir%"] = "examples/FQ_burn/input"
    settings["%space_file%"] = "Burn.lcp"
    settings["%initial_fire_shape%"] = "FQ_burn.shp"
    settings["%start_time%"] = "05 04 0000"
    settings["%end_time%"] = "05 04 0500"
    # settings["%timestep%"] = "5"
    settings["%distance_res%"] = "5.0"
    settings["%perimeter_res%"] = "5.0"
    settings["%params%"] = macro_replace(settings, params)
    # starting with temporal extent
    for i in range(1, 91, 3):
        settings["%timestep%"] = f"{i}"
        execute_simulator(generate_input_files(settings))


def run_experiment_pr(settings: dict):
    settings["%space_dir%"] = "examples/FQ_burn/input"
    settings["%space_file%"] = "Burn.lcp"
    settings["%initial_fire_shape%"] = "FQ_burn.shp"
    settings["%start_time%"] = "05 04 0000"
    settings["%end_time%"] = "05 04 0500"
    settings["%timestep%"] = "5"
    # settings["%distance_res%"] = "5.0"
    # settings["%perimeter_res%"] = "5.0"
    settings["%params%"] = macro_replace(settings, params)
    # starting with temporal extent
    for i in range(1, 91, 3):
        dr = i if i < 5 else 5
        settings["%distance_res%"] = f"{dr}"
        settings["%perimeter_res%"] = f"{i}"
        execute_simulator(generate_input_files(settings))


def run_experiment_dr(settings: dict):
    settings["%space_dir%"] = "examples/FQ_burn/input"
    settings["%space_file%"] = "Burn.lcp"
    settings["%initial_fire_shape%"] = "FQ_burn.shp"
    settings["%start_time%"] = "05 04 0000"
    settings["%end_time%"] = "05 04 0500"
    settings["%timestep%"] = "5"
    # settings["%distance_res%"] = "5.0"
    # settings["%perimeter_res%"] = "50"
    settings["%params%"] = macro_replace(settings, params)
    perimeter_res = [1, 15, 30, 45, 60, 75, 90]
    for pr in perimeter_res:
        settings["%perimeter_res%"] = f"{pr}"
        settings["%preset_output_path%"] = f"%base_path%/examples/FQ_burn/output/perimeter_res_{pr}/burn_%params%/"
        for dr in range(1, pr + 2, 2):
            settings["%distance_res%"] = f"{dr}"
            execute_simulator(generate_input_files(settings))


def read_latency(read_path: str, project: str):
    filename = project + '_Timings.txt'
    # for file in df_file_list:
    file = os.path.join(read_path, filename)
    with open(file, 'r') as f:
        lines = f.readlines()
    measures = [lines[9], lines[10], lines[11], lines[14], lines[15], lines[16], lines[-1]]
    measures = [s.strip().split(":")[1] for s in measures]
    measures[-1] = measures[-1].split(" Seconds")[0]
    # print(time)
    return measures


def read_experiment_latencies(root_dir: str):
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            print(read_latency(os.path.join(subdir, file), "Burn"))


def get_start_cell_id(geography_file: str) -> int:
    return 0


def get_cell_id_results(input_file: str, cell_mapping_file: str) -> dict:
    cell_id = get_start_cell_id(input_file)
    mappings = open(cell_mapping_file, 'r').readlines()
    results = dict()
    row_num = 0
    for row in mappings:
        row_num += 1
        if row_num == 1:
            continue
        for cell in row.split(',')[:-1]:
            results[cell_id] = True if cell == '1' else False
            cell_id += 1
    return results


def update_table(cell_id: int, fire_presence: bool) -> None:
    command = f"UPDATE fire_map SET fire_presence = {1 if fire_presence else 0} WHERE cell_id = {cell_id}"
    repo.execute(command)


def get_parameter_order(epoch_minutes: int, duration_in_epochs: int) -> list:
    chosen_parameters = list()
    for time in range(epoch_minutes, duration_in_epochs * epoch_minutes + 1, epoch_minutes):
        filtered_parameters = {key: value for (key, value) in input_parameters.items() if value[0] < time}
        chosen_parameters.append(max(filtered_parameters, key=lambda k: filtered_parameters[k][1]))
    return chosen_parameters


def call_simulator(settings: dict, parameter: tuple) -> None:
    # set parameters
    settings["%start_time%"] = "05 04 0000"
    # end = start + time extent
    settings["%end_time%"] = "05 04 0200"
    settings["%timestep%"] = str(parameter[1])
    settings["%distance_res%"] = str(parameter[2])
    settings["%perimeter_res%"] = str(parameter[3])
    execute_simulator(generate_input_files(settings))


def update_results(input_file: str, output_path: str) -> None:
    for output_file in os.listdir(output_path):
        file = os.path.join(output_path, output_file)
        print(f"Updating results for {file}")
        cell_results = get_cell_id_results(input_file, file)
        for cell_id in cell_results.keys():
            if cell_id < 25:  # for demo only
                update_table(cell_id, cell_results[cell_id])


def get_fire_perimeters_filename(output_path: str) -> str:
    return f"{output_path}Burn_Perimeters.shp"


def drive(epoch: int, duration: int) -> None:
    settings = dict()
    init(settings)
    add_execution_params(settings)
    print("Getting best order of simulator control parameters")
    parameters = get_parameter_order(epoch, duration)
    for parameter in parameters:
        print(f"Calling simulator for: {parameter}")
        call_simulator(settings, parameter)
        cell_mappings_path = f"{settings['%output_path%']}cell_mappings/"
        generate_cell_mapping(get_fire_perimeters_filename(settings["%output_path%"]),
                              cell_mappings_path, x_min, y_min, x_max, y_max, unit)
        update_results(settings["%input_file_name%"], cell_mappings_path)


if __name__ == '__main__':
    drive(2, 2)

    # create_rxfire("", "", [2])
    # create_ignition_fire("./lcp/LCP_LF2022_FBFM13_220_CONUS.GeoJSON", "./lcp/barrier.shp", latitude_size=0.1,
    #                      longitude_size=0.1, horizontal_offset=0.05, vertical_offset=-0.05)
    # read_experiment_latencies(
    #     "/home/sriram/code/farsite/farsite_simulator/examples/FQ_burn/output/timestep/")
    # parameters = dict()
    # init(parameters)
    # add_execution_params(parameters)
    # execute_simulator(generate_input_files(parameters))
    # run_experiment(parameters)
