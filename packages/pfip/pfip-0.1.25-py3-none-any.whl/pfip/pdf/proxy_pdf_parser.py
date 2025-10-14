import os.path
import PyPDF2
from loguru import logger
from pydantic import Field, model_validator
from typing import Dict, Optional
from typing_extensions import Self

from pfip.base.constant import TFileExt, TPdf
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult
from pfip.base.util.file_util import get_file_name_without_ext
from pfip.pdf.analyse.pdf_analyser import PdfAnalyser
from pfip.pdf.scanned.scanned_pdf_parser import ScannedPdfParser
from pfip.pdf.text.text_pdf_parser import TextPdfParser


class ProxyPdfParser(Parser):
    text_fast_mode: bool = True
    embedding_server_url: Optional[str] = None
    paddle_server_url: Optional[str] = None
    handlers: Dict[TPdf, Parser] = Field(default={}, exclude=True)
    pdf_analyser: PdfAnalyser = Field(default=PdfAnalyser(), exclude=True)

    @model_validator(mode='after')
    def init(self) -> Self:
        text_pdf_parser = TextPdfParser(
            fast_mode=self.text_fast_mode,
            embedding_server_url=self.embedding_server_url,
            paddle_server_url=self.paddle_server_url
        )
        self.handlers[TPdf.TEXT] = text_pdf_parser
        if self.paddle_server_url:
            scanned_pdf_parser = ScannedPdfParser(
                paddle_server_url=self.paddle_server_url,
                embedding_server_url=self.embedding_server_url
            )
            self.handlers[TPdf.SCANNED] = scanned_pdf_parser
        else:
            logger.warning("paddle_server_url未设置,扫描版PDF处理器将不可用...")
        return self

    def support(self, file_ext: str) -> bool:
        return file_ext.lower() == TFileExt.PDF

    def repair_pdf(self, file_path: str) -> str:
        home_dir = self.get_home_dir(file_path)
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            basename = get_file_name_without_ext(file_path)
            repaired_path = os.path.join(home_dir, basename + "_repaired.pdf")
            with open(repaired_path, "wb") as new_file:
                writer = PyPDF2.PdfWriter()
                for i in range(len(reader.pages)):
                    writer.add_page(reader.pages[i])
                writer.write(new_file)
            return repaired_path

    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        try:
            analyse_result = self.pdf_analyser(file_path)
        except Exception as e:
            logger.error(f"{e}, {file_path} 打开失败，修复该文档格式不规范问题")
            file_path = self.repair_pdf(file_path)
            analyse_result = self.pdf_analyser(file_path)

        pdf_type = analyse_result.pdf_type
        assert pdf_type in self.handlers, f"不支持的处理类型:{pdf_type}"
        logger.info("{}==>pdf类型为{}", file_path, pdf_type)
        handler = self.handlers.get(pdf_type)
        return handler(file_path, analyse_result=analyse_result)
