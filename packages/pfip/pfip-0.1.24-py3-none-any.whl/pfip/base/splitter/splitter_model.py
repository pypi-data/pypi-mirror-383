from typing import List

from pydantic import BaseModel, Field, computed_field

from pfip.base.constant import TSentence, TChunk
from pfip.base.parser.parser_model import TitleNode, AtomItem


class Sentence(BaseModel):
    item_type: TSentence
    content: str


class TextSentence(Sentence):
    item_type: TSentence = TSentence.TEXT


class ImageSentence(Sentence):
    item_type: TSentence = TSentence.IMAGE
    image_url: str


class TableSentence(Sentence):
    item_type: TSentence = TSentence.TABLE
    table_html: str


class Chunk(BaseModel):
    content: str
    title: TitleNode
    items: List[AtomItem] = Field(exclude=True)
    sentences: List[Sentence] = []
    chunk_type: TChunk
    start_page: int
    end_page: int

    @computed_field
    def title_id(self) -> str:
        return self.title.id

class SplitResult(BaseModel):
    titles: List[TitleNode]
    chunks: List[Chunk]
