from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self

from pfip.base.errors import UnSupportedFileType
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult, AtomItem, TitleNode
from pfip.base.splitter.base import ChunkSplitter, SentenceSplitter
from pfip.base.splitter.sentence_splitter import CommonSentenceSplitter, PdfSentenceSplitter, MdSentenceSplitter
from pfip.base.splitter.splitter_model import SplitResult, Chunk
from pfip.base.splitter.title_splitter import TitleChunkSplitter, PdfTitleChunkSplitter
from pfip.base.util.file_util import get_file_ext
from pfip.excel.excel_parser import ExcelParser
from pfip.md.md_parser import MDParser
from pfip.pdf.proxy_pdf_parser import ProxyPdfParser
from pfip.ppt.ppt_parser import PPTParser
from pfip.txt.txt_parser import TxtParser
from pfip.web.html_parser import HtmlParser
from pfip.word.word_parser import WordParser


class ProcessResult(BaseModel):
    content: str = Field(description="全文内容")
    items: List[AtomItem]
    titles: List[TitleNode]
    chunks: List[Chunk]


class ParserFactory(BaseModel):
    text_fast_mode: bool = True
    embedding_server_url: Optional[str] = Field(default=None)
    paddle_server_url: Optional[str] = Field(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)
    parsers: List[Parser] = Field(default=[], exclude=True)

    @model_validator(mode="after")
    def init(self) -> Self:
        self.parsers.append(ExcelParser())
        self.parsers.append(HtmlParser())
        self.parsers.append(MDParser())
        self.parsers.append(PPTParser())
        self.parsers.append(TxtParser())
        self.parsers.append(WordParser())
        self.parsers.append(
            ProxyPdfParser(
                text_fast_mode=self.text_fast_mode,
                embedding_server_url=self.embedding_server_url,
                paddle_server_url=self.paddle_server_url
            )
        )
        return self

    def get(self, file_path: str) -> Parser:
        ext = get_file_ext(file_path)
        for parser in self.parsers:
            if parser.support(ext):
                return parser
        raise UnSupportedFileType(f"不支持的文件类型:{ext}")


class ChunkSplitterFactory(BaseModel):
    splitters: List[ChunkSplitter] = Field(default=[], exclude=True)

    @model_validator(mode="after")
    def init(self) -> Self:
        self.splitters.append(PdfTitleChunkSplitter())
        self.splitters.append(TitleChunkSplitter())

    def get(self, file_path: str) -> ChunkSplitter:
        ext = get_file_ext(file_path)
        for splitter in self.splitters:
            if splitter.support(ext):
                return splitter
        raise UnSupportedFileType(f"不支持的文件类型:{ext}")


class SentenceSplitterFactory(BaseModel):
    splitters: List[SentenceSplitter] = Field(default=[], exclude=True)

    @model_validator(mode="after")
    def init(self) -> Self:
        self.splitters.append(MdSentenceSplitter())
        self.splitters.append(PdfSentenceSplitter())
        self.splitters.append(CommonSentenceSplitter())

    def get(self, file_path: str) -> SentenceSplitter:
        ext = get_file_ext(file_path)
        for splitter in self.splitters:
            if splitter.support(ext):
                return splitter
        raise UnSupportedFileType(f"不支持的文件类型:{ext}")


class PanshiFileIntelligentProcess(BaseModel):
    text_fast_mode: bool = True
    embedding_server_url: Optional[str] = Field(default=None)
    paddle_server_url: Optional[str] = Field(default=None)
    parser_factory: ParserFactory = Field(default=None, exclude=True)
    chunk_splitter_factory: ChunkSplitterFactory = Field(default=None, exclude=True)
    sentence_splitter_factory: SentenceSplitterFactory = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def init(self) -> Self:
        self.parser_factory = ParserFactory(
            text_fast_mode=self.text_fast_mode,
            embedding_server_url=self.embedding_server_url,
            paddle_server_url=self.paddle_server_url
        )
        self.chunk_splitter_factory = ChunkSplitterFactory()
        self.sentence_splitter_factory = SentenceSplitterFactory()

    def parse(self, file_path: str, **kwargs) -> ParseResult:
        """
            只解析
            word:
                converted_pdf_path : 当文档是word时,需要传递word对应的pdf文件,用于修复页码信息
        """
        parser = self.parser_factory.get(file_path)
        return parser(file_path, **kwargs)

    def split(self, file_path: str, result: ParseResult) -> SplitResult:
        chunk_splitter = self.chunk_splitter_factory.get(file_path)
        sentence_splitter = self.sentence_splitter_factory.get(file_path)
        chunks: List[Chunk] = chunk_splitter(result)
        for chunk in chunks:
            sentences = sentence_splitter(chunk)
            chunk.sentences = sentences
        return SplitResult(
            titles=result.titles,
            chunks=chunks
        )

    def process(self, file_path: str, **kwargs) -> ProcessResult:
        """
        word:
            converted_pdf_path : 当文档是word时,需要传递word对应的pdf文件,用于修复页码信息
        """
        parse_result = self.parse(file_path, **kwargs)
        split_result = self.split(file_path, parse_result)
        return ProcessResult(
            content=parse_result.content,
            items=parse_result.items,
            titles=split_result.titles,
            chunks=split_result.chunks
        )
