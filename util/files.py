import csv
import shutil
from pathlib import Path

import simplejson as json

from util.strings import *


def generate_file(template_file: Path, name_template: str, output_path: str, settings: dict):
    with open(template_file, 'r') as template:
        file_content = template.read()

    macros = get_template_substitutes(settings)
    file_content = macro_replace_with_substitutes(macros, file_content)
    filename = (Path(output_path).resolve()
                / sanitise_filename(macro_replace_with_substitutes(macros, name_template)))
    with open(filename, 'w') as file:
        file.write(file_content)
    return filename


def sanitise_filename(name: str):
    file = Path(name)
    return sanitise(file.stem, [' ', '.'], '_') + file.suffix


def create_path_str(path: str) -> Path:
    path_setup = Path(path).resolve()
    path_setup.mkdir(parents=True, exist_ok=True)
    return path_setup


def create_path(path: Path) -> None:
    path.resolve().mkdir(parents=True, exist_ok=True)


def read(path: Path, delimiter: str = ",") -> (dict, [list]):
    lines = list()
    with open(path, "r") as file:
        columns = file.readline().split(delimiter)
        schema = {columns[i].strip(): i for i in range(0, len(columns))}
        for line in file:
            lines.append(line.strip('\n').split(','))
    return schema, lines


def merge(paths: [Path], merged_file: Path, headers: bool = True) -> None:
    header_written = False
    with merged_file.open("a+") as full_file:
        for path in paths:
            if (not path.exists()) or path.stat().st_size == 0:
                continue
            with path.open("r") as part_file:
                first_line = next(part_file)
                if headers and not header_written:
                    full_file.write(first_line)
                    header_written = True
                full_file.write(part_file.read())


def write_line(file_path: Path, text: str) -> None:
    with file_path.open('a+') as file:
        file.write(text + "\n")
        file.flush()


def write_list_to_line(file_path: Path, content: list, column_delimiter: str = comma) -> None:
    write_line(file_path, column_delimiter.join([str(value) for value in content]))


def write_lines(file_path: Path, lines: list, mode: str = "w+") -> None:
    with file_path.open(mode) as file:
        file.writelines("\n".join(str(line) for line in lines))
        file.flush()


def write_json(file_path: Path, data, mode: str = "w") -> None:
    with file_path.open(mode, encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def write_csv(file_path: Path, data, delimiter: str = ",", mode: str = "w") -> None:
    with file_path.open(mode) as file:
        writer = csv.writer(file, delimiter=delimiter)
        writer.writerows(data)


def get_files_like(path: Path, name_pattern: str) -> [Path]:
    contents = path.glob(name_pattern)
    measure_files = [c for c in contents if c.is_file()]
    return measure_files


def copy(source: Path, destination: Path, report_error: bool = False):
    try:
        shutil.copyfile(source, destination)
    except shutil.SameFileError as e:
        if report_error:
            raise e


def prefix_path(prefix: Path, relative_path):
    return str(prefix.resolve() / relative_path) + "/"
