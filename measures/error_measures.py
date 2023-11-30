import logging
import math
import statistics
from _decimal import Decimal


logger = logging.getLogger()


def get_error(coarse_value: Decimal, dataset: [Decimal], interpolate) -> dict:
    value = interpolate(coarse_value, dataset)
    errors = dict()
    for key in row_error_types.keys():
        errors[key] = row_error_types[key]([(value - d, d) for d in dataset])
    return errors


row_error_types = {
    "absolute": lambda values: Decimal(statistics.fmean([abs(value[0]) for value in values])),
    "spercent": lambda values: Decimal(statistics.fmean([abs(value[0])/((abs(value[1]) + abs(value[0])) / 2)
                                                        for value in values]))
}


def aggregate(dataset: [(Decimal, Decimal)], error_type: str) -> Decimal:
    return measure_types[error_type](dataset)


measure_types = {
    "mae": lambda values: Decimal(statistics.fmean([value["absolute"] for value in values])),
    "mse": lambda values: Decimal(statistics.fmean([value["absolute"]**2 for value in values])),
    "rmse": lambda values: math.sqrt(measure_types["mse"](values)),
    "sum": lambda values: sum([value["absolute"] for value in values]),
    "mape": lambda values: Decimal(statistics.fmean([value["spercent"] for value in values]))
}
