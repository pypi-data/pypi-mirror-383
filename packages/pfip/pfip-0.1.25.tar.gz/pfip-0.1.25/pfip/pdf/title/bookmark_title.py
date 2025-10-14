from typing import List

import fitz

from pfip.base.parser.parser_model import TitleNode, AtomItem
from pfip.pdf.title.base import TitleExtractor


class BookMarkTitleExtractor(TitleExtractor):
    def __call__(self, file_path: str, items: List[AtomItem] = []) -> List[TitleNode]:
        titles = []
        with fitz.open(file_path) as pdf:
            for index, entry in enumerate(pdf.get_toc()):
                item = TitleNode(
                    title_level=entry[0],
                    title=entry[1],
                    page_number=entry[2],
                    sn=index + 1
                )
                titles.append(item)
        return titles
