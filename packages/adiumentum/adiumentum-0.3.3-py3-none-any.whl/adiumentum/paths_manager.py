from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

from pydantic import BaseModel


# class PathsManager:
#     @abstractmethod
#     def setup(self) -> None: ...

#     @classmethod
#     @abstractmethod
#     def auto(cls, root_dir: Path): ...

#     @classmethod
#     @abstractmethod
#     def read(cls, config_file_path: Path) -> Self: ...

#     @abstractmethod
#     def write(self, config_file_path: Path) -> None: ...



class PathsManager(BaseModel, ABC):
    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> Self:
        """
        Create directories first if they do not already exist.
        """
        ...

    @classmethod
    @abstractmethod
    def auto(cls, root_dir: Path, **kwargs) -> Self:
        """
        Create directories and files in the default location if they do not alreay exist.
        """
        ...


    @classmethod
    @abstractmethod
    def read(cls, config_file_path: Path) -> Self:
        ...
    
    @abstractmethod
    def write(self, config_file_path: Path) -> None:
        ...

    @staticmethod
    def ensure_file_exists(p: Path, content_if_empty: str = "") -> Path:
        if not p.exists():
            p.touch()
            if content_if_empty:
                p.write_text(content_if_empty)
        return p

    @staticmethod
    def ensure_directory_exists(p: Path) -> Path:
        for parent in p.parents:
            if not parent.exists():
                parent.mkdir()
        if not p.exists():
            p.mkdir()
        return p
