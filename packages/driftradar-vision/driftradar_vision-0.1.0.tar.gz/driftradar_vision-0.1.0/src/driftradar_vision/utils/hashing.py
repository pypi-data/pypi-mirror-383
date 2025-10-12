from __future__ import annotations

from collections.abc import Iterable
from hashlib import blake2b


def merkle_hash(items: Iterable[bytes]) -> str:
    h = blake2b(digest_size=32)
    for it in items:
        h.update(it)
    return h.hexdigest()
