import os
from abc import ABC, abstractmethod
from typing import List

import fitz
from loguru import logger
from pandas import DataFrame
from pydantic import BaseModel
from pymupdf import Page

from pfip.base.errors import UnImplementException
from pfip.base.parser.parser_model import AtomItem, ImageAtomItem, TextAtomItem, TextPDFTableAtomItem, Location
from pfip.base.util.str_util import clean_str_keep_spaces


class TextPdfElementHandler(ABC, BaseModel):
    @abstractmethod
    def run(self, doc, page_num: int, page: Page, home_dir: str) -> List[AtomItem]:
        raise UnImplementException()


class TextPdfParagraphHandler(TextPdfElementHandler):

    def run(self, doc, page_num: int, page: Page, home_dir: str) -> List[TextAtomItem]:
        rtn = []
        text_dict = page.get_text("dict")
        for block in text_dict["blocks"]:
            if "lines" in block:
                block_text = ""
                block_bbox = block["bbox"]
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                block_text = clean_str_keep_spaces(block_text)
                if block_text:
                    item = TextAtomItem.instance(block_text, page_num)
                    item.location = Location(x0=block_bbox[0], y0=block_bbox[1], x1=block_bbox[2], y1=block_bbox[3])
                    rtn.append(item)
        return rtn


class TextPdfTableHandler(TextPdfElementHandler):
    COL_MIN_NUM: int = 2
    """表格最小列数量"""

    def _is_regular_table(self, df: DataFrame) -> bool:
        """是否是正确的表格.库普遍存在解决错误的情况"""
        # 最小列数判断
        if len(df.columns.tolist()) < self.COL_MIN_NUM:
            return False
        return True

    def run(self, doc, page_num: int, page: Page, home_dir: str) -> List[TextPDFTableAtomItem]:
        rtn = []
        tables = page.find_tables()
        height = page.rect.height
        for table_index, table in enumerate(tables):
            df = table.to_pandas()
            if not self._is_regular_table(df):
                continue
            table_item = TextPDFTableAtomItem(
                df=df,
                page_height=height,
                start_page=page_num,
                end_page=page_num
            )
            bbox = table.bbox
            table_item.location = Location(x0=bbox[0], y0=bbox[1], x1=bbox[2], y1=bbox[3])
            rtn.append(table_item)
        return rtn


class TextPdfImageHandler(TextPdfElementHandler):
    MIN_AREA: int = 50 * 100

    def _is_invalid_image(self, image_area: float, page_area: float) -> bool:
        """
            is_small 去除非常小的图片,比如说logo等
            is_big 去除非常大的图片
        """
        is_small = self.MIN_AREA > image_area
        is_big = image_area / page_area > 0.9
        return is_small or is_big

    def run(self, doc, page_num: int, page: Page, home_dir: str) -> List[ImageAtomItem]:
        rtn = []
        img_list = page.get_images(full=True)
        page_area = page.rect.height * page.rect.width
        for image_index, image in enumerate(img_list):
            try:
                xref = image[0]
                img_info = doc.extract_image(xref)
                if not page.get_image_rects(xref):
                    continue
                img_rect = page.get_image_rects(xref)[0]
                width = img_rect[2] - img_rect[0]
                height = img_rect[3] - img_rect[1]
                flag = self._is_invalid_image(width * height, page_area)
                if not img_info or flag:
                    continue
                image_path = os.path.join(home_dir, f"page_{page_num}_image_{image_index + 1}.png")
                pix = fitz.Pixmap(doc, xref)
                # 检查色彩空间并转换
                if pix.colorspace is None:
                    pix = fitz.Pixmap(fitz.csRGB, pix)  # 处理无色彩空间的图像
                elif pix.colorspace.name not in ("DeviceRGB", "DeviceGray"):
                    try:
                        pix = fitz.Pixmap(fitz.csRGB, pix)  # 尝试转换为RGB
                    except Exception as e:
                        pix = None
                if pix is not None:
                    pix.save(image_path)
                item = ImageAtomItem(
                    image_url=image_path,
                    content=None,
                    start_page=page_num,
                    end_page=page_num
                )
                item.location = Location(x0=img_rect[0], y0=img_rect[1], x1=img_rect[2], y1=img_rect[3])
                rtn.append(item)
            except Exception as e:
                logger.error(e)
        return rtn
