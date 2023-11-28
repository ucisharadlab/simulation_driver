import math
import statistics
from _decimal import Decimal


def get_error(coarse_value: Decimal, dataset: [Decimal], interpolate, error_type: str) -> Decimal:
    value = interpolate(coarse_value, dataset)
    return aggregate([(value - d, d) for d in dataset], error_type)


def aggregate(dataset: [(Decimal, Decimal)], error_type: str) -> Decimal:
    return measure_types[error_type](dataset)


measure_types = {
    "mae": lambda values: Decimal(statistics.fmean([abs(value[0]) for value in values])),
    "mse": lambda values: Decimal(statistics.fmean([value[0]**2 for value in values])),
    "rmse": lambda values: math.sqrt(measure_types["mse"](values)),
    "sum": lambda values: sum([abs(value[0]) for value in values]),
    "mape": lambda values: Decimal(statistics.fmean([abs(value[0])/value[1] for value in values]))
}
