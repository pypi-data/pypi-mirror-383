from abc import abstractmethod
from pathlib import Path
from typing import Self


class PathsManager:
    @abstractmethod
    def setup(self) -> None: ...

    @classmethod
    @abstractmethod
    def auto(cls, root_dir: Path): ...

    @classmethod
    @abstractmethod
    def read(cls, config_file_path: Path) -> Self: ...

    @abstractmethod
    def write(self, config_file_path: Path) -> None: ...
