from datetime import datetime
from pathlib import Path


def make_timestamp(places: int = 3) -> str:
    dt = datetime.now()
    if places > 0:
        idx: int | None = min(0, int(places) - 6) or None
        return dt.strftime("%Y-%m-%d_%H:%M:%S.%f")[:idx]
    return dt.strftime("%Y-%m-%d_%H:%M:%S")


def insert_timestamp(p: Path | str) -> Path:
    new_path = str(p)

    if "." in new_path:
        base, suffix = new_path.rsplit(".", 1)
        return Path(f"{base}__{make_timestamp()}.{suffix}")

    return Path(f"{new_path}__{make_timestamp()}")
