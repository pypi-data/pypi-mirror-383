import json
import os
import shutil
from pathlib import Path
from typing import Literal

from .timestamping import make_timestamp
from .typing_utils import JSONDict, JSONList


def list_full(directory: str | Path, ending: str = "") -> list[Path]:
    directory = Path(directory)
    return sorted([directory / file for file in os.listdir(directory) if file.endswith(ending)])


def read_raw(json_path: Path) -> str:
    with open(json_path, encoding="utf-8") as f:
        return f.read()


def back_up_json(original_path: Path, backup_dir: Path | None) -> None:
    if not backup_dir:
        return
    backup_path = backup_dir / original_path.name.replace(".json", f"__{make_timestamp()}.json")
    if original_path.exists():
        shutil.copy(original_path, backup_path)


def read_json(json_path: Path, backup_dir: Path | None = None) -> JSONDict | JSONList:
    back_up_json(json_path, backup_dir)
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def write_json(
    python_obj: JSONDict | JSONList | bytes,
    json_path: Path,
    backup_dir: Path | None = None,
    mode: Literal["w", "a"] = "w",
) -> None:
    if mode not in {"w", "a"}:
        raise ValueError(f"Invalid mode: '{mode}'")
    back_up_json(json_path, backup_dir)
    if mode == "a":
        existing = read_json(json_path)
        if isinstance(existing, list) and isinstance(existing, list):
            python_obj = existing + python_obj
        elif isinstance(existing, list) and isinstance(existing, list):
            python_obj = existing | python_obj
        else:
            raise ValueError("Data types do not match.")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(python_obj, f, ensure_ascii=False, indent=4)


def write_raw(text: str, file_path: Path) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def write_raw_bytes(text: bytes, json_path: Path) -> None:
    with open(json_path, "wb") as f:
        f.write(text)
