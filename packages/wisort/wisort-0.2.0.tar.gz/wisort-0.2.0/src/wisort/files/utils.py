from pathlib import Path


def creation_time(p: Path):
    return p.stat().st_birthtime


def file_size(p: Path):
    return p.stat().st_size


def is_empty(p: Path):
    return file_size(p) == 0
