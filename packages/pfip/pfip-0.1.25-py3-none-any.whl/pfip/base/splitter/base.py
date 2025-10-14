from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, ConfigDict

from pfip.base.errors import UnImplementException
from pfip.base.parser.parser_model import ParseResult
from pfip.base.splitter.splitter_model import Chunk, Sentence


class ChunkSplitter(ABC, BaseModel):
    """chunk切分处理器"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    max_chunk_size: int = 2000

    @abstractmethod
    def support(self, file_ext: str) -> bool:
        return False

    @abstractmethod
    def __call__(self, parse_result: ParseResult) -> List[Chunk]:
        raise UnImplementException("未实现...")


class SentenceSplitter(ABC, BaseModel):
    """sentence切分处理器"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    max_sentence_size: int = 80

    @abstractmethod
    def support(self, file_ext: str) -> bool:
        return False

    @abstractmethod
    def __call__(self, chunk: Chunk) -> List[Sentence]:
        raise UnImplementException("未实现...")
