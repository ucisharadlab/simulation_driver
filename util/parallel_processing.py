import logging
from multiprocessing import Process, Queue, current_process

import log
from util.range_util import bucketize


def run_processes(function, params: list, process_count: int = 1, static_params: dict = None):
    logging.info("Running %d instances of %s", process_count, function.__name__)
    buckets = bucketize(params, process_count)

    queue = Queue(-1)
    log_listener = Process(target=log.listen, args=(queue, log.configure))
    log_listener.start()

    processes = list()
    for i in range(0, process_count):
        process = Process(target=setup_and_run, name=f"Process-{i}", args=(queue, buckets[i], static_params, function))
        process.bucket_id = i
        processes.append(process)
        process.start()
    for process in processes:
        process.join()

    queue.put_nowait(None)
    log_listener.join()


def setup_and_run(queue, bucket, static_params, run):
    process_name = current_process().name
    log.configure_worker(queue)
    logger = logging.getLogger(process_name)
    logger.info(f"Process starting")
    run(bucket, static_params)
    logger.info(f"Process complete")
