comma = ","
tab = "\t"
underscore = "_"
colon = ":"


def macro_replace(macros: dict, initial_text: str) -> str:
    for key in macros.keys():
        if key not in initial_text:
            continue
        if type(macros[key]) is not list and type(macros[key]) is not tuple and type(macros[key]) is not dict:
            initial_text = initial_text.replace(key, macros[key])
            continue
        initial_text = initial_text.replace(key, collate(macros[key]))
    return initial_text


def sanitise(string: str, remove: [str], replacement: str) -> str:
    sanitised = string
    for r in remove:
        sanitised = sanitised.replace(r, replacement)
    return sanitised


def collate(items, separator: str = "\n") -> str:
    # TODO if needed: make recursive if more than one level of nesting is needed
    if len(items) == 0:
        return ""
    if type(next(iter(items), None)) is not dict:
        return separator.join(items)
    return separator.join([separator.join(item.values()) for item in items])
