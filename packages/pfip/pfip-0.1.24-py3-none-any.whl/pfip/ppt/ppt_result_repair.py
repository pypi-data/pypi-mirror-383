from typing import List

from pydantic import BaseModel

from pfip.base.constant import TAtomItem
from pfip.base.parser.parser_model import AtomItem


class PPTRePair(BaseModel):


    @staticmethod
    def run(items: List[AtomItem]) -> List[AtomItem]:
        title_items_with_idx = [(idx, item) for idx, item in enumerate(items) if item.item_type == TAtomItem.TITLE]
        for idx, title in title_items_with_idx:
            if idx + 1 >= len(items):
                continue
            next_item = items[idx + 1]
            if title.content == next_item.content:
                items[idx + 1] = None
        return [item for item in items if item]
