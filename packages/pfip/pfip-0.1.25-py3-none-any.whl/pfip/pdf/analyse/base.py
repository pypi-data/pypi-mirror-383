from typing import List

from pydantic import BaseModel

from pfip.base.constant import TPdf
from pfip.base.util.rectangle import RectangleHelper
from pfip.base.util.str_util import clean_str


class PdfAnaLyserResult(BaseModel):
    pdf_type: TPdf
    """pdf类型"""
    valid_page_start_index: int = 0
    """有效页面起始索引"""
    odd_header_y1: float | None = None
    """奇数页页眉最下方的y轴坐标"""
    even_header_y1: float | None = None
    header_list: List[str] = []
    """偶数页页眉最下方的y轴坐标"""
    odd_footer_y0: float | None = None
    """奇数页页脚最上方的y轴坐标"""
    even_footer_y0: float | None = None
    """偶数页页脚最上方的y轴坐标"""
    footer_list: List[str] = []


class PdfLineBox(BaseModel):
    bottom_left: tuple[float, float]
    top_right: tuple[float, float]
    content: str


class PdfRectBox(BaseModel):
    line_boxs: List[PdfLineBox]

    @classmethod
    def from_pdf_dict(cls, rect_dict, y0: float) -> "PdfRectBox":
        line_boxs = []
        for block in rect_dict["blocks"]:
            if block['type'] == 0:
                for line in block["lines"]:
                    line_bbox = line["bbox"]
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                    line_box = PdfLineBox(
                        bottom_left=(line_bbox[0], line_bbox[1] + y0),
                        top_right=(line_bbox[2], line_bbox[3] + y0),
                        content=clean_str(line_text)
                    )

                    line_boxs.append(line_box)
        return cls(line_boxs=line_boxs)


def get_rect_content(boxs: List[PdfRectBox], rect_box: tuple[float, float, float, float]) -> List[str]:
    """
        boxs: 一个box代表一个页面
        从box获取包含在矩形rect_box的所有文本内容
    """
    rect_angle_helper = RectangleHelper(
        bottom_left=(rect_box[0], rect_box[1]),
        top_right=(rect_box[2], rect_box[3]),
    )
    page_contents = []
    for box in boxs:
        content = ""
        for line_box in box.line_boxs:
            flag = rect_angle_helper.intersection(
                bottom_left=line_box.bottom_left,
                top_right=line_box.top_right
            )
            if flag:
                content += line_box.content
        page_contents.append(content)
    return page_contents


def get_analyse_pages(total_page_num: int, max_analyse_page_num: int) -> tuple[
    List[int], List[int]]:
    """获取待分析的页码: 奇数页码与偶数页码"""
    odd_pages = []
    even_pages = []
    # 跳过前面可能不规范的页码
    start_page_num = max(min(total_page_num - max_analyse_page_num, 10), 0)
    end_page_num = min(total_page_num, start_page_num + max_analyse_page_num)
    for page_num in range(start_page_num, end_page_num):
        if page_num % 2 != 0:
            odd_pages.append(page_num)
        else:
            even_pages.append(page_num)
    return odd_pages, even_pages
