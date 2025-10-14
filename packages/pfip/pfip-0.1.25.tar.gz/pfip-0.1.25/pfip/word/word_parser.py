from typing import List, Any

from docx import Document

from pfip.base.constant import TFileExt, TAtomItem, CONVERTED_PDF_PATH_KEY
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult, AtomItem, TitleNode, TitleAtomItem
from pfip.base.parser.repair import ImageDescRepair, TableDescRepair
from pfip.word.auto_num_helper import WordAutoNumHelper
from pfip.word.word_ele_handler import WordElementHandler, WordParagraphHandler, WordTitleHandler, WordImageHandler, \
    WordTableHandler
from pfip.word.word_result_repair import PageNumRepair


class WordParser(Parser):
    """
        暂不支持的内容:
            1)超链接提取
            2)表格中的选择框
    """
    ele_handlers: List[WordElementHandler] = [
        WordTitleHandler(), WordImageHandler(), WordTableHandler()
    ]
    """word元素处理器集合"""
    fallback_handler: WordParagraphHandler = WordParagraphHandler()
    """兜底的处理器"""
    page_num_repair: PageNumRepair = PageNumRepair()
    image_desc_repair: ImageDescRepair = ImageDescRepair()
    table_desc_repair: TableDescRepair = TableDescRepair()

    def support(self, file_ext: str) -> bool:
        return file_ext.lower() == TFileExt.DOCX

    def parse_one(self, doc: Document, ele: Any, home_dir: str, auto_num_helper: WordAutoNumHelper) -> List[AtomItem]:
        handler = None
        for h in self.ele_handlers:
            if h.support(doc, ele):
                handler = h
                break
        if not handler:
            handler = self.fallback_handler
        return handler.run(doc, ele, home_dir, auto_num_helper)

    def build_titles(self, items: List[AtomItem]) -> List[TitleNode]:
        titles = [item.create_and_connect() for item in items if item.item_type == TAtomItem.TITLE]
        self.fill_titles(titles)
        return titles

    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        doc = Document(file_path)
        home_dir = self.get_home_dir(file_path)
        all_items = []
        auto_num_helper = WordAutoNumHelper(file_path)
        for ele in doc.element.body:
            items = self.parse_one(doc, ele, home_dir, auto_num_helper)
            all_items.extend(items)
        # repair items
        all_items = self.image_desc_repair.run(all_items)
        all_items = self.table_desc_repair.run(all_items)
        if CONVERTED_PDF_PATH_KEY in kwargs:
            converted_pdf_path = kwargs[CONVERTED_PDF_PATH_KEY]
            all_items = self.page_num_repair.run(all_items, converted_pdf_path)
        all_items.insert(0, TitleAtomItem.from_file(file_path))
        titles = self.build_titles(all_items)
        return ParseResult(
            titles=titles,
            items=all_items
        )
