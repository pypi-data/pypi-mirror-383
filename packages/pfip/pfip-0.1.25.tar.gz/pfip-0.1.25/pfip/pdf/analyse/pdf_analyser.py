from pydantic import BaseModel

from pfip.base.constant import TPdf
from pfip.pdf.analyse.base import PdfAnaLyserResult
from pfip.pdf.analyse.footer_analyser import FooterAnalyser
from pfip.pdf.analyse.header_analyser import HeaderAnalyser
from pfip.pdf.analyse.pdf_type_analyser import PdfTypeAnalyser
from pfip.pdf.analyse.valid_page_analyser import ValidPageAnalyser


class PdfAnalyser(BaseModel):
    """pdf分析器"""
    valid_page_analyser: ValidPageAnalyser = ValidPageAnalyser()
    pdf_type_analyser: PdfTypeAnalyser = PdfTypeAnalyser()
    header_analyser: HeaderAnalyser = HeaderAnalyser()
    footer_analyser: FooterAnalyser = FooterAnalyser()

    def analyse_text_pdf(self, pdf_path: str) -> PdfAnaLyserResult:
        valid_page_start_index = self.valid_page_analyser.run(pdf_path)
        odd_header_y1, even_header_y1, header_list = self.header_analyser.run(pdf_path)
        odd_footer_y0, even_footer_y0, footer_list = self.footer_analyser.run(pdf_path)
        return PdfAnaLyserResult(
            pdf_type=TPdf.TEXT,
            valid_page_start_index=valid_page_start_index,
            odd_header_y1=odd_header_y1,
            even_header_y1=even_header_y1,
            header_list=header_list,
            odd_footer_y0=odd_footer_y0,
            even_footer_y0=even_footer_y0,
            footer_list=footer_list
        )

    def __call__(self, pdf_path: str) -> PdfAnaLyserResult:
        pdf_type = self.pdf_type_analyser.run(pdf_path)
        if pdf_type == TPdf.SCANNED:
            return PdfAnaLyserResult(pdf_type=TPdf.SCANNED)
        else:
            return self.analyse_text_pdf(pdf_path)
