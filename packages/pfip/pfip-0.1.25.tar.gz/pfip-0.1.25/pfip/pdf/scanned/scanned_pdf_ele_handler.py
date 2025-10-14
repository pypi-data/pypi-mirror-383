from typing import List, Iterable

from panshi2task.paddle_client import BoxRecItem
from pydantic import BaseModel

from pfip.base.constant import UNKOWN_TITLE_LEVEL
from pfip.base.parser.parser_model import AtomItem, TitleAtomItem, ImageAtomItem, \
    ImageCaptionAtomItem, TextAtomItem, ScannedPDFTableAtomItem


class ScannedPdfElementHandler(BaseModel):
    def run(self, itr: Iterable[BoxRecItem], file_path: str) -> List[AtomItem]:
        rtn = []
        last_page_num = 0
        for rec_item in itr:
            cur_page_number = rec_item.page_num
            if rec_item.type == "title":
                rtn.extend(self.parse_title(rec_item))
            elif rec_item.type == "table":
                rtn.extend(self.parse_table(rec_item))
            elif rec_item.type == "figure":
                rtn.extend(self.parse_image(rec_item))
            elif rec_item.type in ["text", "reference"]:
                rtn.extend(self.parse_text_or_reference(rec_item))
            elif rec_item.type == "figure_caption":
                rtn.extend(self.parse_image_caption(rec_item))
            else:
                continue
            if last_page_num != cur_page_number:
                last_page_num = cur_page_number
        return rtn

    @staticmethod
    def parse_title(rec_item: BoxRecItem) -> List[TitleAtomItem]:
        rtn = []
        if not rec_item.res:
            return rtn
        title: str = ""
        for item in rec_item.res:
            if not item.text:
                continue
            title += item.text
        rtn.append(TitleAtomItem.instance(title, UNKOWN_TITLE_LEVEL, rec_item.page_num))
        return rtn

    @staticmethod
    def parse_text_or_reference(rec_item: BoxRecItem) -> List[TextAtomItem]:
        rtn = []
        if not rec_item.res:
            return rtn

        for item in rec_item.res:
            if not item.text:
                continue
            rtn.append(TextAtomItem.instance(item.text, rec_item.page_num))
        return rtn

    @staticmethod
    def parse_table(rec_item: BoxRecItem) -> List[ScannedPDFTableAtomItem]:
        rtn = []
        if not rec_item.res:
            return rtn

        for item in rec_item.res:
            if not item.table_html:
                continue
            rtn.append(ScannedPDFTableAtomItem.simple(item.table_html, page_num=rec_item.page_num))
        return rtn

    @staticmethod
    def parse_image(rec_item: BoxRecItem) -> List[ImageAtomItem]:
        rtn = []
        if rec_item.img_url:
            rtn.append(ImageAtomItem.simple(rec_item.img_url, "", rec_item.page_num))
        return rtn

    @staticmethod
    def parse_image_caption(rec_item: BoxRecItem) -> List[ImageCaptionAtomItem]:
        if not rec_item.res:
            return []
        image_desc = []
        for item in rec_item.res:
            if not item.text:
                continue
            image_desc.append(item.text)
        image_desc_str = "".join(image_desc)
        return [ImageCaptionAtomItem.simple(image_desc_str, rec_item.page_num)]
