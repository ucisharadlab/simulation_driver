# Method to run farsite ad hoc
#   Find code that calls farSite through CLI
#   Add parameters to it
# create template input file with placeholders
# save with a naming convention
import os

from geography import create_ignition_fire

base_path = '/home/sriram/code/farsite/farsite_simulator'
# base_path = '.'
run_file_path = 'examples/FQ_burn/run_file'
run_file_template = 'runBurn_template.txt'
run_file_name_template = 'runBurn_%params%.txt'
input_file_path = 'examples/FQ_burn/Burn_inputfiles'
input_file_template = 'burn_template.input'
input_file_name_template = 'burn_%params%.input'
params = '%timestep%_%distance_res%_%perimeter_res%_%start_time%_%end_time%'


def generate_input_files(settings: dict):
    settings["%input_file_name%"] = generate_file(input_file_path, input_file_template,
                                                  input_file_name_template, settings)
    settings["%output_path%"] = create_output_path(settings)
    return generate_file(run_file_path, run_file_template, run_file_name_template, settings)


def generate_file(path: str, template_file: str, name_template: str, settings: dict):
    with open(f"{base_path}/{path}/{template_file}", 'r') as template:
        file_content = template.read()

    file_content = macro_replace(settings, file_content)

    file_name = f"{base_path}/{path}/{sanitise_file_name(macro_replace(settings, name_template))}"

    print(file_name)
    # print(file_content)

    with open(file_name, 'w') as file:
        file.write(file_content)

    return file_name


def create_output_path(settings: dict) -> str:
    output_path = settings["%preset_output_path%"]
    output_path = sanitise_file_name(macro_replace(settings, output_path))
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    print(output_path)
    return output_path


def macro_replace(settings: dict, initial_string: str) -> str:
    for key in settings.keys():
        initial_string = initial_string.replace(key, settings[key])
    return initial_string


def sanitise_file_name(name: str) -> str:
    filename, extension = os.path.splitext(name)
    return filename.replace(" ", "_").replace(".", "_") + extension


def execute_simulator(run_file: str):
    cmd = f'{base_path}/src/TestFARSITE {run_file} 2>&1 '
    print(cmd)
    os.system(cmd)
    print(f"Finished simulating for {run_file}")


def init(settings: dict):
    settings["%base_path%"] = base_path
    settings["%run_file_path%"] = run_file_path
    settings["%run_file_template%"] = run_file_template
    settings["%input_file_path%"] = input_file_path
    settings["%input_file_template%"] = input_file_template
    settings["%preset_output_path%"] = f"%base_path%/examples/FQ_burn/output/space_res/burn_%params%/"


def add_execution_params(settings: dict):
    settings["%space_dir%"] = "examples/FQ_burn/input"
    settings["%space_file%"] = "Burn.lcp"
    settings["%initial_fire_shape%"] = "FQ_burn.shp"
    settings["%start_time%"] = "05 04 0000"
    settings["%end_time%"] = "05 04 0200"
    settings["%timestep%"] = "1"
    settings["%distance_res%"] = "5.0"
    settings["%perimeter_res%"] = "5.0"
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
    file = os.path.join(read_path, df_filename)
    with open(file, 'r') as f:
        lines = f.readlines()
    measures = [lines[9], lines[10], lines[11], lines[14], lines[15], lines[16], lines[-1]]
    measures = [l.strip().split(":")[1] for s in measures]
    measures[-1] = measures[-1].split(" Seconds")[0]
    # print(time)
    return measures


def read_experiment_latencies(root_dir: str):
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            print(read_latency(os.path.join(subdir, file), "Burn"))


if __name__ == '__main__':
    create_ignition_fire("./lcp/LCP_LF2022_FBFM13_220_CONUS.GeoJSON", "./lcp/ignition.shp", latitude_size=0.1,
                         longitude_size=0.10, horizontal_offset=0.05, vertical_offset=-0.05)
    # read_experiment_latencies(
    #     "/home/sriram/code/farsite/farsite_simulator/examples/FQ_burn/output/timestep/")
    # parameters = dict()
    # init(parameters)
    # add_execution_params(parameters)
    # execute_simulator(generate_input_files(parameters))
    # run_experiment(parameters)
