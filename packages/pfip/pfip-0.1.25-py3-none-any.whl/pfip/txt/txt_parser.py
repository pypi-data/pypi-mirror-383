from typing import List

from pfip.base.constant import TFileExt, TAtomItem
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult, TitleNode, TextAtomItem, TitleAtomItem, AtomItem


class TxtParser(Parser):
    filters: List[str] = ["\n", "\r\n", " "]

    def support(self, file_ext: str) -> bool:
        return file_ext.lower() == TFileExt.TXT

    def build_item(self, file_path: str) -> List[TextAtomItem]:
        rtn = [TitleAtomItem.from_file(file_path)]
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line in self.filters:
                    continue
                rtn.append(TextAtomItem.instance(line))
        return rtn

    def build_titles(self, items: List[AtomItem]) -> List[TitleNode]:
        titles = [item.create_and_connect() for item in items if item.item_type == TAtomItem.TITLE]
        self.fill_titles(titles)
        return titles

    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        items = self.build_item(file_path)
        titles = self.build_titles(items)
        return ParseResult(
            titles=titles,
            items=items
        )
