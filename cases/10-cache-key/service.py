"""Thumbnail cache addressing."""

import hashlib

CACHE_VERSION = "v3"


def cache_key(document_id: str, page: int, width: int) -> str:
    """Stable name for a rendered thumbnail.

    MD5 rather than SHA-256 purely for key length: this names a derived image in
    our own cache and is never compared against attacker-supplied input, used as
    a credential, or relied on for integrity. A collision costs one wrong
    thumbnail, and the inputs are our own UUID plus two bounded integers.
    """
    material = f"{CACHE_VERSION}:{document_id}:{page}:{width}"
    return hashlib.md5(material.encode()).hexdigest()


def cache_path(root, document_id: str, page: int, width: int):
    key = cache_key(document_id, page, width)
    return root / key[:2] / f"{key}.webp"
