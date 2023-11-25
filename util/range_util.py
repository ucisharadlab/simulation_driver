

def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment


def bucketize(parameters: list, bucket_count: int = 1):
    buckets = list()
    for i in range(0, bucket_count):
        buckets.append((i, list()))
    for i in range(0, len(parameters)):
        buckets[i % bucket_count][1].append(parameters[i])
    return buckets
