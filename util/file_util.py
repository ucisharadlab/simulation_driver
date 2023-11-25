import os
from pathlib import Path

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
