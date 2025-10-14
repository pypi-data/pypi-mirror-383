from typing import List

import pandas as pd

from pfip.base.constant import TFileExt, TAtomItem
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult, TableAtomItem, TitleNode, TitleAtomItem, AtomItem


class ExcelParser(Parser):
    """
        将sheet视为titleNode
        将sheet中的内容视为一个TableAtomItem
        暂不支持的特性:
        1. 不处理excel中的图片
        2. 不支持处理复杂表头
    """

    def support(self, file_ext: str) -> bool:
        return file_ext.lower() in [TFileExt.XLS, TFileExt.XLSX]

    def build_titles(self, items: List[AtomItem]) -> List[TitleNode]:
        title_items = [item for item in items if item.item_type == TAtomItem.TITLE]
        titles = [ti.create_and_connect() for ti in title_items]
        self.fill_titles(titles)
        return titles

    @staticmethod
    def build_items(file_path: str) -> List[AtomItem]:
        items = [TitleAtomItem.from_file(file_path)]
        excel = pd.ExcelFile(file_path)
        sheet_names = excel.sheet_names
        for idx, sheet_name in enumerate(sheet_names):
            all_df = excel.parse(sheet_name)
            df_cleaned = all_df.dropna(how='all')
            if not df_cleaned.empty:
                items.append(TitleAtomItem.instance(sheet_name, 1, idx + 1))
                items.append(TableAtomItem.simple(df_cleaned, page_num=idx + 1))
        return items


    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        items = self.build_items(file_path)
        titles = self.build_titles(items)
        return ParseResult(
            items=items,
            titles=titles
        )
