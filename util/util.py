import os
from pathlib import Path


class FileUtil:
    @staticmethod
    def generate_file(template_file: Path, name_template: str, output_path: str, settings: dict):
        with open(template_file, 'r') as template:
            file_content = template.read()

        file_content = StringUtil.macro_replace(settings, file_content)
        filename = os.path.join(output_path,
                                FileUtil.sanitise_filename(StringUtil.macro_replace(settings, name_template)))

        with open(filename, 'w') as file:
            print(os.getcwd())
            file.write(file_content)
        return filename

    @staticmethod
    def sanitise_filename(name: str):
        filename, extension = os.path.splitext(name)
        return StringUtil.sanitise(filename, [' ', '.'], '_') + extension

    @staticmethod
    def create_path(path: str) -> None:
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def read(path: Path, delimiter: str = ",") -> (dict, [list]):
        lines = list()
        with open(path, "r") as file:
            columns = file.readline().split(delimiter)
            schema = {columns[i].strip(): i for i in range(0, len(columns))}
            for line in file:
                lines.append(line.strip('\n').split(','))
        return schema, lines


class StringUtil:
    comma = ","
    tab = "\t"
    underscore = "_"
    colon = ":"

    @staticmethod
    def macro_replace(macros: dict, initial_text: str) -> str:
        for key in macros.keys():
            if key not in initial_text:
                continue
            if type(macros[key]) is not list and type(macros[key]) is not tuple and type(macros[key]) is not dict:
                initial_text = initial_text.replace(key, macros[key])
                continue
            initial_text = initial_text.replace(key, StringUtil.collate(macros[key]))
        return initial_text

    @staticmethod
    def sanitise(string: str, remove: [str], replacement: str) -> str:
        sanitised = string
        for r in remove:
            sanitised = sanitised.replace(r, replacement)
        return sanitised

    @staticmethod
    def collate(items, separator: str = "\n") -> str:
        # TODO if needed: make recursive if more than one level of nesting is needed
        if len(items) == 0:
            return ""
        if type(next(iter(items), None)) is not dict:
            return separator.join(items)
        return separator.join([separator.join(item.values()) for item in items])


class RangeUtil:
    @staticmethod
    def decimal_range(start, stop, increment):
        while start < stop:
            yield start
            start += increment
