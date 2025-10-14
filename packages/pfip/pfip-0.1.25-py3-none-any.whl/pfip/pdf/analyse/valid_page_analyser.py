import fitz
from loguru import logger
from pydantic import BaseModel
from pymupdf import Page

from pfip.base.util.str_util import remove_empty_lines, clean_str


class ValidPageAnalyser(BaseModel):
    start_valid_page: int = 10
    """有效页校验的最大页码范围"""
    line_num_rule: int = 15
    """每页的行数不能小于10行"""
    text_len_rule: int = 200
    """每页的内容不得少于100个字符"""

    def run(self, pdf_path: str) -> int:
        with fitz.open(pdf_path) as doc:
            try:
                if doc.page_count < self.start_valid_page:
                    return 0
                last_not_valid_page_index = -1
                may_be_start_valid_page = min(self.start_valid_page, doc.page_count)
                for page_index in range(may_be_start_valid_page):
                    page = doc.load_page(page_index)
                    if self.is_valid(page):
                        break
                    else:
                        last_not_valid_page_index = page_index
                return last_not_valid_page_index + 1
            except Exception as e:
                logger.error(e)
                return 0

    def is_valid(self, page: Page) -> bool:
        text: str = page.get_text("text")
        cleaned_text = clean_str(text, except_newline=True)
        lines = remove_empty_lines(cleaned_text.split("\n"))
        line_num = len(lines)
        text_len = len(clean_str(text))
        flag1 = line_num > self.line_num_rule
        flag2 = text_len > self.text_len_rule
        return flag1 and flag2
