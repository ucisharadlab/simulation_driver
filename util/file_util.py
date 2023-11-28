import json
import os
from pathlib import Path

from util import string_util
from util.string_util import *


def generate_file(template_file: Path, name_template: str, output_path: str, settings: dict):
    with open(template_file, 'r') as template:
        file_content = template.read()

    file_content = macro_replace(settings, file_content)
    filename = os.path.join(output_path,
                            sanitise_filename(macro_replace(settings, name_template)))

    with open(filename, 'w') as file:
        print(os.getcwd())
        file.write(file_content)
    return filename


def sanitise_filename(name: str):
    filename, extension = os.path.splitext(name)
    return sanitise(filename, [' ', '.'], '_') + extension


def create_path(path: str) -> None:
    if not os.path.exists(path):
        os.mkdir(path)


def read(path: Path, delimiter: str = ",") -> (dict, [list]):
    lines = list()
    with open(path, "r") as file:
        columns = file.readline().split(delimiter)
        schema = {columns[i].strip(): i for i in range(0, len(columns))}
        for line in file:
            lines.append(line.strip('\n').split(','))
    return schema, lines


def merge(paths: [Path], merged_file: Path) -> None:
    with merged_file.open("a+") as full_file:
        for path in paths:
            with path.open("r") as part_file:
                full_file.write(part_file.read())


def write_line(file_path: Path, text: str) -> None:
    with file_path.open('a+') as file:
        file.write(text + "\n")
        file.flush()


def write_list_to_line(file_path: Path, content: list, column_delimiter: str = string_util.comma) -> None:
    write_line(file_path, column_delimiter.join(content))


def write_lines(file_path: Path, lines: list, mode: str = "w") -> None:
    with file_path.open(mode) as file:
        file.writelines("\n".join(str(line) for line in lines))
        file.flush()


def write_json(file_path: Path, data, mode: str = "w") -> None:
    with file_path.open(mode) as file:
        json.dump(data, file)
