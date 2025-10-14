from typing import List

import fitz
from loguru import logger
from panshi2task.paddle_client import PaddleTaskClient, BoxRecItem
from pydantic import Field, model_validator
from tqdm import tqdm
from typing_extensions import Self

from pfip.base.constant import UNKOWN_TITLE_LEVEL
from pfip.base.parser.parser_model import TitleNode, AtomItem
from pfip.base.util.file_util import get_file_name
from pfip.pdf.title.base import TitleExtractor


class LayoutAnalysisTitleExtractor(TitleExtractor):
    """
        基于版面分析模型的title构建工具.
    """
    paddle_server_url: str
    """paddle服务地址"""
    client: PaddleTaskClient = Field(default=None, exclude=True)
    max_support_pages: int = 30

    @model_validator(mode='after')
    def init(self) -> Self:
        self.client = PaddleTaskClient(self.paddle_server_url)
        return self

    @staticmethod
    def parse_title(rec_item: BoxRecItem) -> List[TitleNode]:
        rtn = []
        if not rec_item.res:
            return rtn
        title: str = ""
        for item in rec_item.res:
            if not item.text:
                continue
            title += item.text
        rtn.append(TitleNode(title=title, title_level=UNKOWN_TITLE_LEVEL))
        return rtn

    def __call__(self, file_path: str, items: List[AtomItem]=[]) -> List[TitleNode]:
        rtn = []
        with fitz.open(file_path) as pdf:
            total_page_num = pdf.page_count
        if total_page_num > self.max_support_pages:
            logger.warning("文字版PDF页码超过{}限制,耗时过长,不支持处理...", self.max_support_pages)
            return rtn
        file_name = get_file_name(file_path)
        progress_bar = tqdm(total=total_page_num, desc=f"版面分析中==>{file_name}")
        last_page_num = 0
        for rec_item in self.client.pdf_structure_bytes(file_path):
            cur_page_number = rec_item.page_num
            if rec_item.type == "title":
                rtn.extend(self.parse_title(rec_item))
            else:
                continue
            if last_page_num != cur_page_number:
                progress_bar.update(cur_page_number - last_page_num)
                last_page_num = cur_page_number
        return rtn
