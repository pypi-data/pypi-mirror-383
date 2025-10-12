from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, get_args

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class Serializable(Generic[T], ABC):
    data: T
    save_path: Path

    load_from_json: bool = True

    @abstractmethod
    def _save_path(self) -> Path:
        pass

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]

    def __init__(self):
        self.save_path = self._save_path()
        self.data = self.load_data()

    def save_data(self, overwrite: bool = True) -> None:
        json_data: str = self.data.model_dump_json(indent=2)
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

        if self.save_path.exists() and not overwrite:
            raise FileExistsError(f"File {self.save_path} already exists and overwrite is False.")

        self.save_path.write_text(json_data)

    def load_data(self) -> T:
        if not self.load_from_json or not self.save_path.exists():
            return self._type_T()
        try:
            return self._type_T.model_validate_json(self.save_path.read_text())
        except:
            raise NotImplementedError("Serializable.data_type is not specified")
