from __future__ import annotations

import time
from contextlib import contextmanager


@contextmanager
def stopwatch(label: str):
    t0 = time.time()
    try:
        yield
    finally:
        dt = time.time() - t0
        print(f"{label} took {dt:.2f}s")
