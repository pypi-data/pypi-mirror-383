import os
from datetime import datetime
from pathlib import Path


def time_created(path: Path | str) -> float:
    return Path(path).stat().st_ctime


def format_time(raw_time: float, places: int = 3) -> str:
    dt = datetime.fromtimestamp(raw_time)
    if places > 0:
        idx: int | None = min(0, int(places) - 6) or None
        return dt.strftime("%Y-%m-%d_%H:%M:%S.%f")[:idx]
    return dt.strftime("%Y-%m-%d_%H:%M:%S")


def time_created_readable(path: Path | str, places: int = 3) -> str:
    # time_created: time.struct_time = time.strptime(time.ctime(time_created(path)))
    return format_time(time_created(path), places=places)


def time_modified(path: Path | str) -> float:
    return Path(path).stat().st_mtime


def time_modified_readable(path: Path | str, places: int = 3) -> str:
    # time_modified: time.struct_time = time.strptime(time.ctime(time_modified(path)))
    return format_time(time_modified(path), places=places)


def first_newer(file1: str | Path, file2: str | Path | tuple[Path, ...] | tuple[str, ...]) -> bool:
    m1 = os.path.getmtime(file1)

    if isinstance(file2, tuple):
        m2 = max(os.path.getmtime(f) for f in file2)
    else:
        m2 = os.path.getmtime(file2)
    return m1 > m2
