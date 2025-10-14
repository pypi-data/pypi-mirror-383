import os
from typing import List

import html2text
from bs4 import BeautifulSoup

from pfip.base.constant import TFileExt, TAtomItem
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult, TextAtomItem, TitleAtomItem, AtomItem, TitleNode
from pfip.base.util.common import remove_whitespace
from pfip.base.util.file_util import get_file_name_without_ext


class HtmlParser(Parser):

    def support(self, file_ext: str) -> bool:
        return file_ext.lower() == TFileExt.HTML

    @staticmethod
    def build_item(file_path: str) -> List[TextAtomItem]:
        rtn = [TitleAtomItem.from_file(file_path)]
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            text_lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(text_lines)
            rtn.append(TextAtomItem.instance(cleaned_text))
        return rtn

    def build_titles(self, items: List[AtomItem]) -> List[TitleNode]:
        titles = [item.create_and_connect() for item in items if item.item_type == TAtomItem.TITLE]
        self.fill_titles(titles)
        return titles

    @staticmethod
    def html2md(file_path: str, home_dir: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        markdown_content = html2text.html2text(html_content)
        md_file_path = os.path.join(home_dir, get_file_name_without_ext(file_path) + "_convert.md")
        with open(md_file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)
        return md_file_path

    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        items = self.build_item(file_path)
        titles = self.build_titles(items)
        return ParseResult(
            titles=titles,
            items=items
        )
