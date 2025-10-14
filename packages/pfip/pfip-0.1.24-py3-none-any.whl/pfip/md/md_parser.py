from collections import deque
from typing import List, Optional

from pydantic import model_validator, Field
from typing_extensions import Self

from pfip.base.constant import TFileExt, TAtomItem
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult, AtomItem, TitleNode, TitleAtomItem
from pfip.md.md_ele_handler import MDElementHandler, MDParagraphHandler, MDTitleHandler, \
    MDTableHandler, MDListHandler, MDCodeHandler, MdHtmlHandler, MDRefHandler


class MDParser(Parser):
    """
        支持code|table|txt|image识别
        按行读取
        status
    """
    ele_handlers: Optional[List[MDElementHandler]] = Field(default=None, exclude=True)
    """md元素处理器集合"""
    fallback_handler: Optional[MDElementHandler] = Field(default=None, exclude=True)
    """兜底的处理器"""

    @model_validator(mode='after')
    def init_handlers(self) -> Self:
        self.fallback_handler = MDParagraphHandler()
        self.ele_handlers = [
            MDRefHandler(), MDTitleHandler(), MDTableHandler(), MDListHandler(), MDCodeHandler(), MdHtmlHandler()
        ]
        return self

    def support(self, file_ext: str) -> bool:
        return file_ext.lower() == TFileExt.MD

    def read(self, file_path: str) -> deque[str]:
        q = deque()
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if not self.is_empty_line(line):
                    q.append(line.strip())
        return q

    def find_ele_handler(self, line: str) -> MDElementHandler:
        for h in self.ele_handlers:
            if h.support(line):
                return h
        return self.fallback_handler

    def parse(self, file_path: str, q: deque[str]) -> List[AtomItem]:
        rtn = [TitleAtomItem.from_file(file_path)]
        while q:
            start_line = q.popleft()
            hander = self.find_ele_handler(start_line)
            rtn.append(hander.run(start_line, q))
        return rtn

    def build_titles(self, items: List[AtomItem]) -> List[TitleNode]:
        titles = [item.create_and_connect() for item in items if item.item_type == TAtomItem.TITLE]
        self.fill_titles(titles)
        return titles

    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        q = self.read(file_path)
        items = self.parse(file_path, q)
        titles = self.build_titles(items)
        return ParseResult(
            items=items,
            titles=titles
        )
