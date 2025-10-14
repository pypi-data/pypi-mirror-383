from typing import List, Dict

from pydantic import Field, model_validator
from typing_extensions import Self

from pfip.base.constant import TAtomItem, TFileExt
from pfip.base.parser.parser_model import TableAtomItem, ImageAtomItem, MDCodeAtomItem, MDListAtomItem, \
    MDRefAtomItem, TextAtomItem, AtomItem, MDHtmlAtomItem
from pfip.base.splitter.base import SentenceSplitter
from pfip.base.splitter.splitter_model import Chunk, Sentence, TableSentence, ImageSentence, TextSentence
from pfip.base.util.character_splitter import RecursiveCharacterTextSplitter, Language


class CommonSentenceSplitter(SentenceSplitter):
    character_text_splitter: RecursiveCharacterTextSplitter = Field(default=None, exclude=True)
    separators: list[str] = ["。", "．", ".", "；", "；", ";", "，", ",", " ", ""]

    @model_validator(mode="after")
    def init(self) -> Self:
        if not self.character_text_splitter:
            self.character_text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.max_sentence_size,
                chunk_overlap=0,
                separators=self.separators
            )
        return self

    def support(self, file_ext: str) -> bool:
        return True

    def custom_deal(self, item: AtomItem) -> List[Sentence]:
        return []

    def __call__(self, chunk: Chunk) -> List[Sentence]:
        sentences = []
        for item in chunk.items:
            if isinstance(item, TextAtomItem):
                sentences.extend(self.text2sentence(item))
            elif isinstance(item, TableAtomItem):
                sentences.append(self.table2sentence(item))
            elif isinstance(item, ImageAtomItem):
                sentences.append(self.image2sentence(item))
            else:
                sentences.extend(self.custom_deal(item))
        return sentences

    def text2sentence(self, item: TextAtomItem) -> List[TextSentence]:
        texts = []
        if len(item.content) > self.max_sentence_size:
            texts.extend(self.character_text_splitter.split_text(item.content))
        else:
            texts.append(item.content)
        return [TextSentence(content=text) for text in texts]

    @staticmethod
    def table2sentence(item: TableAtomItem) -> TableSentence:
        return TableSentence(content=item.table_desc, table_html=item.full_content)

    @staticmethod
    def image2sentence(item: ImageAtomItem) -> ImageSentence:
        return ImageSentence(content=item.full_content, image_url=item.image_url)


class MdSentenceSplitter(CommonSentenceSplitter):
    code_splitters: Dict[Language, RecursiveCharacterTextSplitter] = {}

    @model_validator(mode="after")
    def init_code_splitters(self) -> Self:
        for language in Language:
            language_splitter = RecursiveCharacterTextSplitter.from_language(
                language.HTML,
                chunk_size=self.max_sentence_size,
                chunk_overlap=0
            )
            self.code_splitters[language] = language_splitter
        return self

    def support(self, file_ext: str) -> bool:
        return file_ext == TFileExt.MD

    def custom_deal(self, item: AtomItem) -> List[Sentence]:
        sentences = []
        if isinstance(item, MDListAtomItem):
            sentences.extend(self.mdlist2sentence(item))
        elif isinstance(item, MDCodeAtomItem):
            sentences.extend(self.mdcode2sentence(item))
        elif isinstance(item, MDRefAtomItem):
            sentences.extend(self.mdref2sentence(item))
        elif isinstance(item, MDHtmlAtomItem):
            sentences.extend(self.mdhtml2sentence(item))
        return sentences

    def mdlist2sentence(self, item: MDListAtomItem) -> List[TextSentence]:
        texts = []
        for line in item.content:
            if len(line) > self.max_sentence_size:
                texts.extend(self.character_text_splitter.split_text(line))
            else:
                texts.append(line)
        return [TextSentence(content=text) for text in texts]

    def mdcode2sentence(self, item: MDCodeAtomItem) -> List[TextSentence]:
        texts = []
        content = "\n".join(item.content)
        if len(content) > self.max_sentence_size:
            language = item.language
            if language in self.code_splitters:
                language_splitter = self.code_splitters[language]
                texts.extend(language_splitter.split_text(content))
            else:
                texts.extend(self.character_text_splitter.split_text(content))
        else:
            texts.append(content)
        return [TextSentence(content=text) for text in texts]

    def mdref2sentence(self, item: MDRefAtomItem) -> List[TextSentence]:
        texts = []
        content = "\n".join(item.content)
        if len(content) > self.max_sentence_size:
            texts.extend(self.character_text_splitter.split_text(content))
        else:
            texts.append(content)
        return [TextSentence(content=text) for text in texts]

    def mdhtml2sentence(self, item: MDHtmlAtomItem) -> List[TextSentence]:
        texts = []
        content = "\n".join(item.content)
        if len(content) > self.max_sentence_size:
            texts.extend(self.character_text_splitter.split_text(content))
        else:
            texts.append(content)
        return [TextSentence(content=text) for text in texts]


# noinspection PyTypeChecker
class PdfSentenceSplitter(CommonSentenceSplitter):

    def support(self, file_ext: str) -> bool:
        return file_ext == TFileExt.PDF

    def __call__(self, chunk: Chunk) -> List[Sentence]:
        rtn = []
        group_items = self.group_by_image_and_table(chunk.items)
        for group in group_items:
            if isinstance(group, list):
                rtn.extend(self.items2sentence(group))
            elif isinstance(group, TableAtomItem):
                rtn.append(self.table2sentence(group))
            elif isinstance(group, ImageAtomItem):
                rtn.append(self.image2sentence(group))
            else:
                continue
        return rtn

    @staticmethod
    def group_by_image_and_table(items: List[AtomItem]) -> List[List[AtomItem] | AtomItem]:
        group_items = []
        cache_items = []
        for item in items:
            if item.item_type in [TAtomItem.TABLE, TAtomItem.IMAGE]:
                group_items.append(item)
                if cache_items:
                    group_items.append(cache_items.copy())
                    cache_items = []
            else:
                cache_items.append(item)
        if cache_items:
            group_items.append(cache_items.copy())
        return group_items

    def items2sentence(self, items: List[AtomItem]) -> List[Sentence]:
        lines = [item.content for item in items]
        all_content = "".join(lines)
        split_contents = self.character_text_splitter.split_text(all_content)
        return [TextSentence(content=text) for text in split_contents]
