from typing import List, Dict

from pydantic import BaseModel

from pfip.base.constant import TAtomItem
from pfip.base.parser.parser_model import AtomItem, ImageCaptionAtomItem, TitleNode, TextAtomItem, TitleAtomItem
from pfip.pdf.title.bookmark_title import BookMarkTitleExtractor
from pfip.pdf.title.title_item_connector import TitleConnector


class ImageRepair(BaseModel):
    """
        1)补全图片的描述信息
    """

    @staticmethod
    def _find_image_desc_item(idx: int, items: List[AtomItem]) -> tuple[int, ImageCaptionAtomItem] | tuple[int, None]:
        if idx + 1 < len(items):
            right = items[idx + 1]
            if isinstance(right, ImageCaptionAtomItem):
                return idx + 1, right
        if idx - 1 >= 0:
            left = items[idx - 1]
            if isinstance(left, ImageCaptionAtomItem):
                return idx - 1, left
        return -1, None

    def run(self, items: List[AtomItem]):
        image_item_idxs = []
        need_remove_item_idxs = []
        for idx, item in enumerate(items):
            if item.item_type == TAtomItem.IMAGE:
                image_item_idxs.append(idx)
        for idx in image_item_idxs:
            image_desc_idx, image_desc_item = self._find_image_desc_item(idx, items)
            if image_desc_item:
                items[idx].content = image_desc_item.content
                need_remove_item_idxs.append(image_desc_idx)
        filtered_items = [item for idx, item in enumerate(items) if idx not in need_remove_item_idxs]
        return filtered_items


class BookMarkTitleRepair(BaseModel):
    """
    TODO 问题待修复
    3==>1.1.1 数据的定义和生命周期／1
    2==>1.1 数据工程相关概念／1
    """

    book_mark_extractor: BookMarkTitleExtractor = BookMarkTitleExtractor()
    tconn: TitleConnector

    @staticmethod
    def to_text_item(items: List[AtomItem]) -> List[AtomItem]:
        dealed_items = []
        for item in items:
            if item.item_type == TAtomItem.TITLE:
                text_item = TextAtomItem.model_validate(item.model_dump())
                text_item.item_type = TAtomItem.TEXT
                dealed_items.append(text_item)
            else:
                dealed_items.append(item)
        return dealed_items

    @staticmethod
    def get_candcates(has_index_items: List[tuple[AtomItem, int]], page_numer: int) -> List[tuple[AtomItem, int]]:
        return [item for item in has_index_items if item[0].start_page == page_numer or item[0].end_page == page_numer]


    def run(self, file_path: str, items: List[AtomItem]) -> List[AtomItem]:
        title_nodes = self.book_mark_extractor(file_path)
        if not title_nodes:
            return items
        text_items = self.to_text_item(items)
        has_index_items: List[tuple[AtomItem, int]] = []
        for index, item in enumerate(text_items):
            has_index_items.append((item, index))
        title_conn_pos_dict: Dict[int, TitleNode] = {}

        for title in title_nodes:
            candcates = self.get_candcates(has_index_items, title.page_number)
            new_pos = self.tconn.find_similar_title(title, candcates)
            if new_pos < 0:
                continue
            title_conn_pos_dict[new_pos] = title
        # 替换处理
        final_items = []
        for index, item in enumerate(text_items):
            if index in title_conn_pos_dict:
                title = title_conn_pos_dict[index]
                title_item = TitleAtomItem.instance(title.title, title.title_level, item.start_page)
                final_items.append(title_item)
            else:
                final_items.append(item)
        return final_items
