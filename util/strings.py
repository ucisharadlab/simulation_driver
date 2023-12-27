from datetime import datetime
from string import Template

comma = ","
tab = "\t"
underscore = "_"
colon = ":"


def macro_replace(macros: dict, text: str) -> str:
    if not isinstance(text, str):
        return text
    return Template(text).safe_substitute(get_template_substitutes(macros))


def sanitise(string: str, remove: [str], replacement: str) -> str:
    sanitised = string
    for r in remove:
        sanitised = sanitised.replace(r, replacement)
    return sanitised


def collate(items, separator: str = "\n") -> str:
    if len(items) == 0:
        return ""
    if type(next(iter(items), None)) is not dict:
        return separator.join(items)
    return separator.join([separator.join(item.values()) for item in items])


def get_date_str(date: datetime = datetime.now()):
    return date.strftime("%Y-%m-%d_%H-%M")


def get_template_substitutes(settings: dict) -> dict:
    return {key.replace("%", ""):
            (value if isinstance(value, str) else collate(value))
            for key, value in settings.items()}
