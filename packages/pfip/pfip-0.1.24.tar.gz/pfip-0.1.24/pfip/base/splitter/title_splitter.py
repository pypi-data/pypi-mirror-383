from typing import List, Tuple, Dict

from pydantic import model_validator, Field
from typing_extensions import Self

from pfip.base.constant import TAtomItem, TFileExt, TChunk
from pfip.base.parser.parser_model import ParseResult, AtomItem, TitleNode, TextAtomItem
from pfip.base.splitter.base import ChunkSplitter
from pfip.base.splitter.splitter_model import Chunk
from pfip.base.util.character_splitter import RecursiveCharacterTextSplitter


# noinspection PyTypeChecker
class TitleChunkSplitter(ChunkSplitter):
    """
        基于标题的段落语义切分器
    """
    character_text_splitter: RecursiveCharacterTextSplitter = Field(default=None, exclude=True)
    separators: list[str] = ["\n\n", "\n", "。", "．", ".", "；", ";", "，", ",", " ", ""]

    @model_validator(mode="after")
    def init(self) -> Self:
        if not self.character_text_splitter:
            self.character_text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.max_chunk_size,
                chunk_overlap=0,
                separators=self.separators,
                keep_separator=True
            )
        return self

    def support(self, file_ext: str) -> bool:
        return True

    def __call__(self, parse_result: ParseResult) -> List[Chunk]:
        items_groups = self.group_by_title(parse_result.items)
        chunks = []
        for group in items_groups:
            group_chunks = self.split_group(group)
            chunks.extend(group_chunks)
        # sentence 切分
        return chunks

    @staticmethod
    def group_by_title(items: List[AtomItem]) -> List[Tuple[TitleNode, List[AtomItem]]]:
        """
            根据item_type==TAtomItem.TITLE进行分组,后面的元素为一组，直到遇见下一个TITLE元素
        """

        def add_group(_grouped_items: List, _current_group: List):
            key: str = _current_group[0].title_node
            val = _current_group[1:]
            if len(val):
                _grouped_items.append((key, val))

        grouped_items = []
        current_group = []
        for item in items:
            if item.item_type == TAtomItem.TITLE:
                if current_group:
                    add_group(grouped_items, current_group)
                    current_group = []
            current_group.append(item)
        if current_group:
            add_group(grouped_items, current_group)
        return grouped_items

    def split_group(self, group: Tuple[TitleNode, List[AtomItem]]) -> List[Chunk]:
        def create_chunk_by_cache(title: TitleNode, chunk_items: List[AtomItem]) -> Chunk:
            chunk_content = "\n".join([_item.full_content for _item in chunk_items])
            start_page = chunk_items[0].start_page
            end_page = chunk_items[-1].end_page
            return Chunk(
                title=title,
                content=chunk_content,
                items=chunk_items,
                start_page=start_page,
                end_page=end_page,
                chunk_type=TChunk.TEXT
            )

        def create_chunks_by_one(title: TitleNode, big_item: AtomItem) -> List[Chunk]:
            """
                当一个AtomItem就超过chunk最大限制时,需要再次切分
            """
            if big_item.item_type in [TAtomItem.TABLE, TAtomItem.IMAGE]:
                chunk = Chunk(
                    title=title,
                    content=big_item.full_content,
                    items=[big_item],
                    start_page=big_item.start_page,
                    end_page=big_item.end_page,
                    chunk_type=big_item.item_type
                )
                return [chunk]
            else:
                start_page = big_item.start_page
                end_page = big_item.end_page
                chunk_contents = self.character_text_splitter.split_text(big_item.full_content)
                _chunks = []
                for content in chunk_contents:
                    small_item = TextAtomItem(content=content, start_page=start_page, end_page=end_page)
                    _chunks.append(
                        Chunk(
                            title=title,
                            content=content,
                            items=[small_item],
                            start_page=start_page,
                            end_page=end_page,
                            chunk_type=TChunk.TEXT
                        )
                    )
                return _chunks

        title_node = group[0]
        items: List[AtomItem] = group[1]
        items_cache: List[AtomItem] = []
        items_cache_text_len = 0
        chunks = []
        for idx, item in enumerate(items):
            new_text_len = len(item.full_content)
            if len(item.full_content) > self.max_chunk_size \
                    or item.item_type == TAtomItem.TABLE \
                    or item.item_type == TAtomItem.IMAGE:
                """FIXED:将表格单独切成一个chunk"""
                if len(items_cache) > 0:
                    items_cache_text_len = 0
                    chunks.append(create_chunk_by_cache(title_node, items_cache.copy()))
                    items_cache.clear()
                chunks.extend(create_chunks_by_one(title_node, item))
            elif new_text_len + items_cache_text_len > self.max_chunk_size:
                # 生成chunk 清除缓存
                chunks.append(create_chunk_by_cache(title_node, items_cache.copy()))
                items_cache.clear()
                items_cache.append(item)
                items_cache_text_len = new_text_len
            else:
                items_cache.append(item)
                items_cache_text_len += new_text_len

        if items_cache_text_len > 0:
            chunks.append(create_chunk_by_cache(title_node, items_cache))
        return chunks


class PdfTitleChunkSplitter(TitleChunkSplitter):

    def support(self, file_ext: str) -> bool:
        return TFileExt.PDF.value == file_ext.lower()

    def __call__(self, parse_result: ParseResult) -> List[Chunk]:
        items_groups = self.group_by_title(parse_result.items)
        chunks = []
        for group in items_groups:
            group_chunks = self.split_group(group)
            chunks.extend(group_chunks)
        # sentence 切分
        return chunks

    def split_group(self, group: Tuple[TitleNode, List[AtomItem]]) -> List[Chunk]:
        def build_char_page_index(chunk_items: List[AtomItem]) -> Dict[int, int]:
            """
            构建 char_index=>page_num
            char_index: 字符在整个content中的索引. content是所有chunk_items的content拼接而成
            page_num:页码
            """
            char_page_dict = {}
            append_content = ""
            for _item in chunk_items:
                pre_index = len(append_content)
                assert _item.start_page == _item.end_page
                page_num = _item.start_page
                item_dict = {i: page_num for i in range(pre_index, pre_index + len(_item.full_content) + 1)}
                char_page_dict.update(item_dict)
                append_content += _item.full_content
            return char_page_dict

        def create_chunk_by_cache(title: TitleNode, chunk_items: List[AtomItem]) -> List[Chunk]:
            total_len = 0
            total_content = ""
            for _item in chunk_items:
                total_content += f"{_item.full_content}"
                total_len += len(total_content)
            if total_len > self.max_chunk_size:
                chunk_contents = self.character_text_splitter.split_text(total_content)
                char_page_index = build_char_page_index(chunk_items)
                _chunks = []
                append_part = ""
                for part in chunk_contents:
                    start_page = char_page_index[len(append_part)]
                    end_page = char_page_index[len(append_part) + len(part)]
                    _chunks.append(
                        Chunk(
                            title=title,
                            content=part,
                            items=[TextAtomItem(content=part, start_page=start_page, end_page=end_page)],
                            start_page=start_page,
                            end_page=end_page,
                            chunk_type=TChunk.TEXT
                        )
                    )
                    append_part += part
                return _chunks
            else:
                start_page = chunk_items[0].start_page
                end_page = chunk_items[-1].end_page
                return [Chunk(
                    title=title,
                    content=total_content,
                    items=chunk_items,
                    start_page=start_page,
                    end_page=end_page,
                    chunk_type=TChunk.TEXT
                )]

        def create_chunks_by_one(title: TitleNode, big_item: AtomItem) -> List[Chunk]:
            """
                当一个AtomItem就超过chunk最大限制时,需要再次切分
            """
            if big_item.item_type in [TAtomItem.TABLE, TAtomItem.IMAGE]:
                chunk = Chunk(
                    title=title,
                    content=big_item.full_content,
                    items=[big_item],
                    start_page=big_item.start_page,
                    end_page=big_item.end_page,
                    chunk_type=big_item.item_type
                )
                return [chunk]
            else:
                start_page = big_item.start_page
                end_page = big_item.end_page
                chunk_contents = self.character_text_splitter.split_text(big_item.full_content)
                _chunks = []
                for content in chunk_contents:
                    small_item = TextAtomItem(content=content, start_page=start_page, end_page=end_page)
                    _chunks.append(
                        Chunk(
                            title=title,
                            content=content,
                            items=[small_item],
                            start_page=start_page,
                            end_page=end_page,
                            chunk_type=TChunk.TEXT
                        )
                    )
                return _chunks

        title_node = group[0]
        items: List[AtomItem] = group[1]
        items_cache: List[AtomItem] = []
        chunks = []
        for idx, item in enumerate(items):
            if item.item_type == TAtomItem.TABLE or item.item_type == TAtomItem.IMAGE:
                if items_cache:
                    chunks.extend(create_chunk_by_cache(title_node, items_cache.copy()))
                    items_cache.clear()
                chunks.extend(create_chunks_by_one(title_node, item))
            else:
                items_cache.append(item)
        if items_cache:
            chunks.extend(create_chunk_by_cache(title_node, items_cache.copy()))
        return chunks
