import fitz
from pydantic import BaseModel

from pfip.base.constant import TPdf


class PdfTypeAnalyser(BaseModel):
    max_extract_page_num: int = 20
    """采样的页码数量"""
    scanned_pdf_threshold: float = 0.7

    def run(self, pdf_path: str) -> TPdf:
        """
            如果图片页所占比重超过threshold,则认为是扫描件,反之为文字版
        """
        with fitz.open(pdf_path) as doc:
            total_page_num = doc.page_count
            assert total_page_num != 0
            min_page_num = min(total_page_num, self.max_extract_page_num)
            cur_page = 0
            image_page_num = 0
            for page_num in range(min_page_num):
                p = doc.load_page(page_num)
                if cur_page >= min_page_num:
                    break
                if not p.get_text("text"):
                    image_page_num += 1
                cur_page += 1

            radio = image_page_num / min_page_num
            if radio > self.scanned_pdf_threshold:
                return TPdf.SCANNED
            else:
                return TPdf.TEXT
