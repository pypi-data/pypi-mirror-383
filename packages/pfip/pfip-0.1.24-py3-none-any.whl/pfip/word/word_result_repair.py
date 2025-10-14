import re
from typing import List, Tuple

import PyPDF2
from loguru import logger
from pydantic import BaseModel

from pfip.base.constant import TAtomItem, ROOT_TITLE_LEVEL
from pfip.base.parser.parser_model import AtomItem, WordTitleAtomItem, WordTextAtomItem, TitleAtomItem, TextAtomItem


class PageNumRepair(BaseModel):
    error_page_num: int = 0

    @staticmethod
    def _remove_whitespace(text: str):
        """使用正则表达式去除所有空格和不可见字符"""
        return re.sub(r'\s+', '', text)

    def _read_pdf(self, file_path: str) -> List[str]:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            pages = []
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                pages.append(self._remove_whitespace(page_text))
            return pages

    def _compare(self, content: str, pages: List[str], cur_page_num: int) -> Tuple[int, int]:
        cur_page = pages[cur_page_num - 1]
        if content in cur_page:
            return cur_page_num, cur_page_num
        next_pages = [cur_page]
        for i in range(10):
            if cur_page_num + i >= len(pages):
                break
            next_page = pages[cur_page_num + i]
            next_pages.append(next_page)
            if content in next_page:
                return cur_page_num + i + 1, cur_page_num + i + 1
            elif content in next_pages[-2] + next_page:
                return cur_page_num + i, cur_page_num + i + 1
        return self.error_page_num, self.error_page_num

    @staticmethod
    def get_left_item(idx: int, items: List[AtomItem]) -> tuple[int, AtomItem]:
        cur_idx = idx - 1
        item = None
        while cur_idx >= 0:
            if items[cur_idx].start_page:
                item = items[cur_idx]
                break
            else:
                cur_idx -= 1
        return cur_idx, item

    @staticmethod
    def get_right_item(idx: int, items: List[AtomItem]) -> tuple[int, AtomItem]:
        cur_idx = idx + 1
        item = None
        while cur_idx < len(items):
            if items[cur_idx].start_page:
                item = items[cur_idx]
                break
            else:
                cur_idx += 1
        return cur_idx, item

    def _infer_fail_item(self, idx: int, fail_idxs: List[int], items: List[AtomItem], total_page_num: int):
        """根据上下文的页码信息进行推断"""
        fail_item = items[idx]
        lidx, left = self.get_left_item(idx, items)
        ridx, right = self.get_right_item(idx, items)
        if len(items) == idx + 1:
            right = TextAtomItem.instance("最后一页", page_num=total_page_num)
        if left is None or right is None:
            logger.error("无法修复此元素的页码信息:{}", fail_item.model_dump_json())
            return
        if ridx in fail_idxs:
            # todo 右侧元素也是需要修复的,暂时默认当前元素与前一个元素在同一页，会有误差
            fail_item.start_page = left.end_page
            fail_item.end_page = left.end_page
            return
        page_range = right.start_page - left.end_page
        if page_range > 2:
            logger.error("无法修复此元素的页码信息,相邻元素页码差距过大{},:{}", page_range, fail_item.model_dump_json())
            return
        if fail_item.item_type == TAtomItem.IMAGE:
            # 图片不能跨页
            fail_item.start_page = right.start_page
            fail_item.end_page = right.start_page
        else:
            fail_item.start_page = left.end_page
            fail_item.end_page = right.start_page

    def run(self, items: List[AtomItem], pdf_path: str):
        pages = self._read_pdf(pdf_path)
        fail_idxs = []
        cur_page_num = 1
        for idx, item in enumerate(items):
            if isinstance(item, TitleAtomItem) and item.title_level == ROOT_TITLE_LEVEL:
                continue
            if item.item_type in [TAtomItem.TABLE, TAtomItem.IMAGE]:
                fail_idxs.append(idx)
                continue
            if isinstance(item, WordTitleAtomItem) or isinstance(item, WordTextAtomItem):
                content = self._remove_whitespace(item.without_auto_num_content)
            else:
                content = self._remove_whitespace(item.content)
            start_page, end_page = self._compare(content, pages, cur_page_num)
            if start_page == self.error_page_num:
                fail_idxs.append(idx)
            else:
                item.start_page = start_page
                item.end_page = end_page
                cur_page_num = end_page
        for fail_idx in fail_idxs:
            self._infer_fail_item(fail_idx, fail_idxs, items, len(pages))
        return items
