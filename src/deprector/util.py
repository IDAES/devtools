from collections import defaultdict
import concurrent.futures
import multiprocessing
from typing import (
    Iterable,
    Mapping,
)


def run_in_subprocess(func, args=None, kwargs=None):
    args = args or tuple()
    kwargs = kwargs or dict()
    ctx = multiprocessing.get_context("spawn")

    with concurrent.futures.ProcessPoolExecutor(mp_context=ctx) as ex:
        promise = ex.submit(func, *args, **kwargs)
        res = promise.result()
    return res


def groupby(items: Iterable, by: str, factory=None) -> Mapping:
    grouped = defaultdict(list)
    for item in items:
        key = getattr(item, by)
        grouped[key].append(item)
    if factory:
        return factory(grouped)
    return grouped