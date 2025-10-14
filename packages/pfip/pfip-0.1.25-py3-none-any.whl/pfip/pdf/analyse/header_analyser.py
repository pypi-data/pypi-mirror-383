import re
from difflib import SequenceMatcher
from typing import List

import fitz
from loguru import logger
from pydantic import BaseModel

from pfip.base.util.str_util import remove_empty_lines
from pfip.pdf.analyse.base import get_analyse_pages, PdfRectBox, get_rect_content


class HeaderAnalyser(BaseModel):
    max_analyse_page_num: int = 20
    """用于页眉分析的最大页码数量"""
    start_header_percent: float = 0.2
    """起始的header位置. 从页面高度的x百分比开始"""
    reduce_step_len: int = 20
    """每次缩减的步长大小"""
    min_same_similar_threshold: float = 0.95
    """两个文本被视为相同的最小阈值"""

    def run(self, pdf_path: str) -> tuple[float, float, List[str]]:
        with fitz.open(pdf_path) as doc:
            footer_list = []
            if doc.page_count < 4:
                return 0, 0, []
            odd_pages, even_pages = get_analyse_pages(doc.page_count, self.max_analyse_page_num)
            odd_y1, odd_texts = self.find_header_area(doc, odd_pages)
            even_y1, even_texts = self.find_header_area(doc, even_pages)
            footer_list.extend(odd_texts)
            footer_list.extend(even_texts)
            return odd_y1, even_y1, list(set(footer_list))

    def find_header_area(self, doc, pages: List[int]) -> tuple[float, List[str]]:
        page_mediabox = doc[pages[0]].mediabox
        pdf_height = doc[pages[0]].rect.height
        try:
            boxs = self.extract_pages_header(doc, pages)
            header_area_y1 = pdf_height * self.start_header_percent
            while header_area_y1 > 0:
                rect = fitz.Rect(page_mediabox.x0, 0, page_mediabox.x1, header_area_y1)
                header_texts = get_rect_content(boxs, rect)
                header_texts = [re.sub(r'\d+', "[页码]", t) for t in header_texts]
                header_texts = [re.sub(r'\b[IVXLCDM]+\b', "[页码]", t) for t in header_texts]
                if self.is_header(header_texts):
                    return header_area_y1, header_texts
                header_area_y1 -= self.reduce_step_len
            return 0, []
        except Exception as e:
            logger.error(e)
            return 0, []

    def extract_pages_header(self, doc, pages: List[int]) -> tuple[float, float, List[str]]:
        """抽取指定页码,y1区域的文本信息"""
        boxs = []
        for page_num in pages:
            page = doc[page_num]
            y1 = page.rect.height * self.start_header_percent
            rect = fitz.Rect(page.mediabox.x0, 0, page.mediabox.x1, y1)
            page.set_cropbox(rect)
            box = PdfRectBox.from_pdf_dict(page.get_text("dict"), 0)
            boxs.append(box)
        return boxs

    def is_header(self, header_texts: List[str]) -> bool:
        """是否为页眉"""
        header_texts = remove_empty_lines(header_texts)
        if len(header_texts) < 2:
            return False
        middle_index = len(header_texts) // 2
        middle_element = header_texts[middle_index]
        similar_count = 0
        for ele in header_texts:
            matcher = SequenceMatcher(None, ele, middle_element)
            if matcher.ratio() > self.min_same_similar_threshold:
                similar_count += 1
        radio = (similar_count - 1) / (len(header_texts) - 1)
        if radio == 1:
            return True
        else:
            return False
