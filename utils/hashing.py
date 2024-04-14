import hashlib


def hash_str(string: str):
    return hashlib.sha1(string.encode("utf-8")).hexdigest()