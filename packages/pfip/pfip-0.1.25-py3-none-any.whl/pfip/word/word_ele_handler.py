import os
import uuid
from abc import ABC, abstractmethod
from itertools import groupby
from typing import Any, List

import pandas as pd
from docx import Document
from docx.oxml import CT_Tbl, CT_P
from docx.text.paragraph import Paragraph
from lxml.etree import XPathEvalError
from pydantic import BaseModel

from pfip.base.errors import UnImplementException
from pfip.base.parser.parser_model import AtomItem, TableAtomItem, ImageAtomItem, WordTitleAtomItem, WordTextAtomItem
from pfip.word.auto_num_helper import WordAutoNumHelper


class WordElementHandler(ABC, BaseModel):
    @abstractmethod
    def support(self, doc: Document, ele: Any) -> bool:
        raise UnImplementException()

    @abstractmethod
    def run(self, doc: Document, ele: Any, home_dir: str, auto_num_helper: WordAutoNumHelper) -> List[AtomItem]:
        raise UnImplementException()

    @staticmethod
    def try_get_auto_num(doc: Document, ele: Any, auto_num_helper: WordAutoNumHelper) -> str:
        if not isinstance(ele, CT_P):
            return ""
        paragraph = Paragraph(ele, doc.element.body)
        return auto_num_helper.get_paragraph_num(paragraph)


class WordTitleHandler(WordElementHandler):
    def support(self, doc: Document, ele: Any) -> bool:
        if isinstance(ele, CT_P):
            return ele.style and "Heading" in doc.styles[ele.style].name
        else:
            return False

    def run(self, doc: Document, ele: Any, home_dir: str, auto_num_helper: WordAutoNumHelper) -> List[
        WordTitleAtomItem]:
        style_name = doc.styles[ele.style].name
        title_name = ele.text.strip()
        if not title_name:
            return []
        else:
            auto_num_text = self.try_get_auto_num(doc, ele, auto_num_helper)
            title_name = auto_num_text + title_name
            title_level = style_name.split()[-1]
            title_item = WordTitleAtomItem.instance(title_name, title_level)
            title_item.auto_num = auto_num_text
            return [title_item]


class WordImageHandler(WordElementHandler):

    def support(self, doc: Document, ele: Any) -> bool:
        try:
            return len(ele.xpath('.//pic:pic')) > 0
        except XPathEvalError:
            return False


    def run(self, doc: Document, ele: Any, home_dir: str, auto_num_helper: WordAutoNumHelper) -> List[ImageAtomItem]:
        image_items = []
        image_ids = ele.xpath('.//a:blip/@r:embed')
        for img_id in image_ids:
            image_part = doc.part.related_parts[img_id]
            image_path = os.path.join(home_dir, str(uuid.uuid4()) + ".png")
            with open(image_path, "wb") as f:
                f.write(image_part.blob)
            image_items.append(ImageAtomItem.simple(image_url=image_path))
        return image_items


class WordTableHandler(WordElementHandler):
    def support(self, doc: Document, ele: Any) -> bool:
        return isinstance(ele, CT_Tbl)

    @staticmethod
    def adjust_table(lines: List[List[Any]]) -> List[List[Any]]:
        # 获取列的基准数量
        sorted_lines = sorted(lines, key=lambda x: len(x))
        grouped_lines = {key: list(group) for key, group in groupby(sorted_lines, key=lambda x: len(x))}
        base_col_num = max(grouped_lines, key=lambda x: len(grouped_lines[x]))
        # 多退少补
        rtn = []
        for line in lines:
            adjust_num = len(line) - base_col_num
            if adjust_num == 0:
                pass
            elif adjust_num > 0:
                for _ in range(adjust_num):
                    line.pop()
            else:
                for _ in range(abs(adjust_num)):
                    line.append("")
            rtn.append(line)
        return rtn

    def run(self, doc: Document, ele: Any, home_dir: str, auto_num_helper: WordAutoNumHelper) -> List[TableAtomItem]:
        lines = []
        for row in ele.tr_lst:
            line = []
            for c in row.tc_lst:
                cell_val = []
                for p in c.p_lst:
                    auto_num_text = self.try_get_auto_num(doc, p, auto_num_helper)
                    cell_val.append(auto_num_text + p.text)
                line.append("".join(cell_val))
            lines.append(line)
        adjust_lines = self.adjust_table(lines)
        df = pd.DataFrame(adjust_lines[1:], columns=adjust_lines[0])
        table_item = TableAtomItem.simple(df)
        return [table_item]


class WordParagraphHandler(WordElementHandler):
    def support(self, doc: Document, ele: Any) -> bool:
        return isinstance(ele, CT_P)

    def run(self, doc: Document, ele: Any, home_dir: str, auto_num_helper: WordAutoNumHelper) -> List[WordTextAtomItem]:
        if ele.text:
            auto_num_text = self.try_get_auto_num(doc, ele, auto_num_helper)
            text = auto_num_text + ele.text.strip()
            item = WordTextAtomItem.instance(text)
            item.auto_num = auto_num_text
            return [item]
        else:
            return []
