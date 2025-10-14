from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, ConfigDict

from pfip.base.errors import UnImplementException
from pfip.base.parser.parser_model import TitleNode, AtomItem


class TitleExtractor(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def __call__(self, file_path: str, items: List[AtomItem]) -> List[TitleNode]:
        raise UnImplementException("未实现...")
