import re
from difflib import SequenceMatcher
from typing import List

import fitz
from loguru import logger
from pydantic import BaseModel

from pfip.base.util.str_util import remove_empty_lines
from pfip.pdf.analyse.base import get_analyse_pages, PdfRectBox, get_rect_content


class FooterAnalyser(BaseModel):
    max_analyse_page_num: int = 20
    """用于页脚分析的最大页码数量"""
    start_footer_percent: float = 0.8
    """起始的footer位置. 从页面高度的x百分比开始"""
    add_step_len: int = 20
    """每次增加的步长大小"""
    min_same_similar_threshold: float = 0.9
    """两个文本被视为相同的最小阈值"""

    def run(self, pdf_path: str) -> tuple[float, float, List[str]]:
        with fitz.open(pdf_path) as doc:
            footer_list = []
            if doc.page_count < 4:
                pdf_height = doc[0].rect.height
                return pdf_height, pdf_height, []
            odd_pages, even_pages = get_analyse_pages(doc.page_count, self.max_analyse_page_num)
            odd_y0, odd_texts = self.find_footer_area(doc, odd_pages)
            even_y0, even_texts = self.find_footer_area(doc, even_pages)
            footer_list.extend(odd_texts)
            footer_list.extend(even_texts)
            return odd_y0, even_y0, list(set(footer_list))

    def find_footer_area(self, doc, pages: List[int]) -> tuple[float, List[str]]:
        page_mediabox = doc[pages[0]].mediabox
        pdf_height = doc[pages[0]].rect.height
        try:
            boxs = self.extract_pages_footer(doc, pages)
            footer_area_y0 = pdf_height * self.start_footer_percent
            while footer_area_y0 < pdf_height - self.add_step_len:
                rect = fitz.Rect(page_mediabox.x0, footer_area_y0, page_mediabox.x1, pdf_height)
                footer_texts = get_rect_content(boxs, rect)
                footer_texts = [re.sub(r'\d+', "[页码]", t) for t in footer_texts]
                footer_texts = [re.sub(r'\b[IVXLCDM]+\b', "[页码]", t) for t in footer_texts]

                if self.is_footer(footer_texts):
                    return footer_area_y0, footer_texts
                footer_area_y0 += self.add_step_len
            return pdf_height, []
        except Exception as e:
            logger.error(e)
            return pdf_height, []

    def extract_pages_footer(self, doc, pages: List[int]) -> List[PdfRectBox]:
        """抽取指定页码,y0区域的文本信息"""
        boxs = []
        for page_num in pages:
            page = doc[page_num]
            y0 = page.rect.height * self.start_footer_percent
            rect = fitz.Rect(page.mediabox.x0, y0, page.mediabox.x1, page.rect.height)
            page.set_cropbox(rect)
            box = PdfRectBox.from_pdf_dict(page.get_text("dict"), y0)
            boxs.append(box)
        return boxs

    def is_footer(self, footer_texts: List[str]) -> bool:
        """是否为页脚"""
        footer_texts = remove_empty_lines(footer_texts)
        if len(footer_texts) < 2:
            return False
        middle_index = len(footer_texts) // 2
        middle_element = footer_texts[middle_index]
        similar_count = 0
        for ele in footer_texts:
            matcher = SequenceMatcher(None, ele, middle_element)
            if matcher.ratio() > self.min_same_similar_threshold:
                similar_count += 1
        radio = (similar_count - 1) / (len(footer_texts) - 1)
        if radio == 1:
            return True
        else:
            return False
