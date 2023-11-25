import statistics
from _decimal import Decimal


def get_error(coarse_value: Decimal, dataset: [Decimal], interpolate) -> Decimal:
    value = interpolate(coarse_value, dataset)
    return aggregate([value - d for d in dataset], 'sum')


def aggregate(dataset: [Decimal], error_type: str) -> Decimal:
    return measure_types[error_type](dataset)


def get_absolute_mean(values: [Decimal]) -> Decimal:
    return Decimal(statistics.fmean([abs(value) for value in values]))


def get_squares_mean(values: [Decimal]) -> Decimal:
    return Decimal(statistics.fmean([value**2 for value in values]))


measure_types = {
    "mae": get_absolute_mean,
    "mse": get_squares_mean,
    "sum": lambda values: sum(values)
}
