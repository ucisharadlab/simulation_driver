import os


class FileUtil:
    @staticmethod
    def generate_file(template_file: str, name_template: str, output_path: str, settings: dict):
        with open(f"{template_file}", 'r') as template:
            file_content = template.read()

        file_content = StringUtil.macro_replace(settings, file_content)
        filename = f"{output_path}/{FileUtil.sanitise_filename(StringUtil.macro_replace(settings, name_template))}"

        with open(filename, 'w') as file:
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


class StringUtil:
    @staticmethod
    def macro_replace(macros: dict, initial_string: str) -> str:
        for key in macros.keys():
            initial_string = initial_string.replace(key, macros[key])
        return initial_string

    @staticmethod
    def sanitise(string: str, remove: [str], replacement: str) -> str:
        sanitised = string
        for r in remove:
            sanitised = sanitised.replace(r, replacement)
        return sanitised
