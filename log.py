import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

import settings

log_format = "%(asctime)s %(processName)s %(module)s %(levelname)s: %(message)s"


def init():
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[logging.StreamHandler()]
    )
    configure()
    logging.getLogger().info("Logger initialized")


def get_log_file_name():
    current_date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = Path(settings.LOG_FILE_PATH).resolve() / f"driver_{current_date_str}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def configure():
    log_path = Path(settings.LOG_FILE_PATH).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(str(log_path), 'a', 100_000_000, 10)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.addHandler(handler)


def listen(queue, setup):
    setup()
    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def configure_worker(queue):
    handler = logging.handlers.QueueHandler(queue)
    logger = logging.getLogger()
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
