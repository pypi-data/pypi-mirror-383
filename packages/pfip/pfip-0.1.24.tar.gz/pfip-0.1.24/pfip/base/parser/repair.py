import re
from typing import List, Tuple

from pydantic import BaseModel

from pfip.base.constant import TAtomItem
from pfip.base.parser.parser_model import AtomItem, TextAtomItem
from pfip.base.util.str_util import clean_str


class ImageDescRepair(BaseModel):
    pattern: str = r"^图\d+.{1,40}$"

    def _find_image_desc_item(self, idx: int, items: List[AtomItem]) -> Tuple[int, AtomItem | None]:
        if idx + 1 < len(items):
            right = items[idx + 1]
            content = clean_str(right.content)
            if isinstance(right, TextAtomItem) and re.match(self.pattern, content):
                return idx + 1, right
        if idx - 1 >= 0:
            left = items[idx - 1]
            content = clean_str(left.content)
            if isinstance(left, TextAtomItem) and re.match(self.pattern, content):
                return idx - 1, left
        return -1, None

    def run(self, items: List[AtomItem]) -> List[AtomItem]:
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


class TableDescRepair(BaseModel):
    pattern: str = r"^表\d+.{1,40}$"

    def _find_table_desc_item(self, idx: int, items: List[AtomItem]) -> Tuple[int, AtomItem | None]:
        if idx + 1 < len(items):
            right = items[idx + 1]
            content = clean_str(right.content)
            if isinstance(right, TextAtomItem) and re.match(self.pattern, content):
                return idx + 1, right
        if idx - 1 >= 0:
            left = items[idx - 1]
            content = clean_str(left.content)
            if isinstance(left, TextAtomItem) and re.match(self.pattern, content):
                return idx - 1, left
        return -1, None

    def run(self, items: List[AtomItem]) -> List[AtomItem]:
        table_item_idxs = []
        need_remove_item_idxs = []
        for idx, item in enumerate(items):
            if item.item_type == TAtomItem.TABLE:
                table_item_idxs.append(idx)
        for idx in table_item_idxs:
            table_desc_idx, table_desc_item = self._find_table_desc_item(idx, items)
            if table_desc_item:
                items[idx].content = table_desc_item.content
                need_remove_item_idxs.append(table_desc_idx)
        filtered_items = [item for idx, item in enumerate(items) if idx not in need_remove_item_idxs]
        return filtered_items
