import importlib


def get_class(full_name: str):
    module_name = full_name.rsplit('.', 1)[0]
    class_name = full_name.rsplit('.', 1)[1]
    return getattr(importlib.import_module(module_name), class_name)


def get_instance(full_class_name: str):
    class_type = get_class(full_class_name)
    return class_type()
