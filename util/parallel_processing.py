from multiprocessing import Pool

from util.range_util import bucketize


def run_parallel_processes(function, params: list, process_count: int = 1, static_params: dict = None):
    buckets = bucketize(params, process_count)
    with Pool(process_count) as pool:
        pool.map(function, buckets, static_params)
