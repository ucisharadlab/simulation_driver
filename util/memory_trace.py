import linecache
import logging
import tracemalloc
from pathlib import Path

logger = logging.getLogger()


def start():
    tracemalloc.start()


def log(snapshot=None, key_type="lineno", limit=5):
    if not snapshot:
        snapshot = tracemalloc.take_snapshot()
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    logger.info("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = Path(frame.filename)
        logger.info("#%s: %s:%s: %.1f KiB"
                    % (index, filename.relative_to(filename.parent.parent), frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            logger.info('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        logger.info("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    logger.info("Total allocated size: %.1f KiB" % (total / 1024))
