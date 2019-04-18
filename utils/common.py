import hashlib


def get_md5(bs: bytes) -> str:
    md5 = hashlib.md5()
    md5.update(bs)
    return md5.hexdigest()
