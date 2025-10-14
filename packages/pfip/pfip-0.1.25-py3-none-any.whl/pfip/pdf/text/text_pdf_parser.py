from typing import Optional, List, Self

import fitz
from loguru import logger
from pydantic import Field, model_validator
from pymupdf import Page, Rect, _format_g
from tqdm import tqdm

from pfip.base.constant import TFileExt, TAtomItem
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult, TitleAtomItem, AtomItem, TitleNode
from pfip.base.util.file_util import get_file_name
from pfip.pdf.analyse.base import PdfAnaLyserResult
from pfip.pdf.text.text_pdf_ele_handler import TextPdfElementHandler, TextPdfParagraphHandler, TextPdfTableHandler, \
    TextPdfImageHandler
from pfip.pdf.text.text_pdf_result_repair import TextPdfRepair, TextPdfTitleRepair
from pfip.pdf.title.base import TitleExtractor
from pfip.pdf.title.bookmark_title import BookMarkTitleExtractor
from pfip.pdf.title.layout_analysis_title import LayoutAnalysisTitleExtractor
from pfip.pdf.title.title_item_connector import TitleConnector
from pfip.pdf.title.toc_page_title import TocPageTitleExtractor


class TextPdfParser(Parser):
    fast_mode: bool = True
    paddle_server_url: Optional[str] = None
    embedding_server_url: Optional[str] = None
    ele_handlers: List[TextPdfElementHandler] = Field(default=[], exclude=True)
    title_extractors: List[TitleExtractor] = Field(default=[], exclude=True)
    text_pdf_repair: TextPdfRepair = Field(default=TextPdfRepair(), exclude=True)
    title_repair: TextPdfTitleRepair = Field(default=None, exclude=True)

    @model_validator(mode='after')
    def init(self) -> Self:
        # handlers
        self.ele_handlers.append(TextPdfParagraphHandler())
        self.ele_handlers.append(TextPdfTableHandler())
        self.ele_handlers.append(TextPdfImageHandler())
        # title_extractors
        self.title_extractors.append(BookMarkTitleExtractor())
        self.title_extractors.append(TocPageTitleExtractor())
        if self.fast_mode:
            logger.warning("快速模式,基于版面分析的标题提取组件将不启用...")
            logger.warning("快速模式,标题修复组件将不启用...")
        else:
            if self.paddle_server_url:
                self.title_extractors.append(LayoutAnalysisTitleExtractor(paddle_server_url=self.paddle_server_url))
            else:
                logger.warning("paddle_server_url未设置,基于版面分析的标题提取组件将不可用...")
            if self.embedding_server_url:
                connect = TitleConnector(embedding_server_url=self.embedding_server_url)
                self.title_repair = TextPdfTitleRepair(tconn=connect)
            else:
                logger.warning("embedding_server_url未设置,标题修复组件不可用...")
        return self

    def support(self, file_ext: str) -> bool:
        return file_ext == TFileExt.PDF

    def extract_titles(self, file_path: str, items: List[AtomItem]) -> List[TitleNode]:
        rtn = []
        for title_extractor in self.title_extractors:
            nodes = title_extractor(file_path, items)
            if nodes:
                rtn.extend(nodes)
                break
        return rtn

    def build_titles(self, items: List[AtomItem]) -> List[TitleNode]:
        titles: List[TitleNode] = [item.create_and_connect() for item in items if item.item_type == TAtomItem.TITLE]
        self.fill_titles(titles)
        return titles

    @staticmethod
    def set_crop_box(doc, page_index: int, page: Page, analyse_result: PdfAnaLyserResult):
        """
            裁剪掉页眉页脚
        """
        if page_index % 2 == 0:
            # 偶数页索引(索引从0计算)
            header_y1 = analyse_result.even_header_y1
            footer_y0 = analyse_result.even_footer_y0
        else:
            header_y1 = analyse_result.odd_header_y1
            footer_y0 = analyse_result.odd_footer_y0

        rect = (
            0,
            header_y1,
            page.rect.width,
            footer_y0
        )
        try:
            mb = page.mediabox
            rect = Rect(rect[0], mb.y1 - rect[3], rect[2], mb.y1 - rect[1])
            doc.xref_set_key(page.xref, "CropBox", f"[{_format_g(tuple(rect))}]")
        except ValueError as e:
            logger.warning(e)

    def one_process(self, home_dir: str, file_path: str, analyse_result: PdfAnaLyserResult):
        rtn = []
        with fitz.open(file_path) as doc:
            file_name = get_file_name(file_path)
            for index in tqdm(range(doc.page_count), desc=file_name):
                if analyse_result:
                    if index < analyse_result.valid_page_start_index:
                        continue
                    page = doc.load_page(index)
                    self.set_crop_box(doc, index, page, analyse_result)
                else:
                    page = doc.load_page(index)
                page_num = index + 1
                for handler in self.ele_handlers:
                    rtn.extend(handler.run(doc, page_num, page, home_dir))
        return rtn

    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        if kwargs.get("analyse_result"):
            analyse_result: PdfAnaLyserResult = kwargs.get("analyse_result")
        else:
            analyse_result = None
        # 解析处理
        home_dir = self.get_home_dir(file_path)
        items = self.one_process(home_dir, file_path, analyse_result)
        # 修复items
        items = self.text_pdf_repair.run(items)
        assert len(items) > 0, "空的pdf,没有可解析的元素"
        # 标题处理
        title_candcates = self.extract_titles(file_path, items)
        if self.title_repair:
            items = self.title_repair.run(title_candcates, items)
        items.insert(0, TitleAtomItem.from_file(file_path, mkpos=True))
        titles = self.build_titles(items)
        return ParseResult(
            items=items,
            titles=titles
        )
