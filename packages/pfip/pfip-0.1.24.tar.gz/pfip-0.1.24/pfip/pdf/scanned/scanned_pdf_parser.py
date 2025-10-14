from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from panshi2task.paddle_client import PaddleTaskClient
from pydantic import Field, model_validator
from tqdm import tqdm
from typing_extensions import Self

from pfip.base.constant import TFileExt, TAtomItem
from pfip.base.parser.base import Parser
from pfip.base.parser.parser_model import ParseResult, TitleNode, AtomItem, TitleAtomItem
from pfip.pdf.pdf_splitter import PdfSplitter
from pfip.pdf.scanned.scanned_pdf_ele_handler import ScannedPdfElementHandler
from pfip.pdf.scanned.scanned_pdf_result_repair import ImageRepair, BookMarkTitleRepair
from pfip.pdf.title.title_item_connector import TitleConnector


class ScannedPdfParser(Parser):
    paddle_server_url: str
    """paddle服务地址"""
    embedding_server_url: Optional[str] = None
    thread_pool_num: int = 5
    client: PaddleTaskClient = Field(default=None, exclude=True)
    handler: ScannedPdfElementHandler = Field(default=ScannedPdfElementHandler(), exclude=True)
    image_repair: ImageRepair = Field(default=ImageRepair(), exclude=True)
    title_repair: BookMarkTitleRepair = Field(default=None, exclude=True)
    pdf_splitter: PdfSplitter = PdfSplitter(max_split_pdf_num=5)
    thread_pool: ThreadPoolExecutor = None  # 初始化线程池

    @model_validator(mode='after')
    def init(self) -> Self:
        self.client = PaddleTaskClient(self.paddle_server_url)
        connect = TitleConnector(embedding_server_url=self.embedding_server_url)
        self.title_repair = BookMarkTitleRepair(tconn=connect)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.thread_pool_num)
        return self

    def __del__(self):
        if hasattr(self, 'thread_pool') and self.thread_pool:
            self.thread_pool.shutdown()


    def support(self, file_ext: str) -> bool:
        return file_ext == TFileExt.PDF

    def build_titles(self, items: List[AtomItem]) -> List[TitleNode]:
        titles: List[TitleNode] = [item.create_and_connect() for item in items if item.item_type == TAtomItem.TITLE]
        self.fill_titles(titles)
        return titles

    def process_one(self, file_path: str) -> tuple[int, List[AtomItem]]:
        _itr = self.client.pdf_structure_bytes(file_path)
        file_start_page, _ = self.pdf_splitter.get_page_area_from_name(file_path)
        items = self.handler.run(_itr, file_path)
        for item in items:
            item.start_page = item.start_page + file_start_page
            item.end_page = item.end_page + file_start_page
        return file_start_page, items

    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        home_dir = self.get_home_dir(file_path)
        split_pdf_paths = self.pdf_splitter.split(file_path, home_dir)
        futures = [self.thread_pool.submit(self.process_one, path) for path in split_pdf_paths]
        results = []
        for future in tqdm(as_completed(futures), total=len(futures)):
            result = future.result()
            results.append(result)
        sorted_results = sorted(results, key=lambda x: x[0])
        items = []
        for sorted_result in sorted_results:
            items.extend(sorted_result[1])
        items = self.image_repair.run(items)
        items = self.title_repair.run(file_path, items)
        items.insert(0, TitleAtomItem.from_file(file_path, mkpos=True))
        titles = self.build_titles(items)
        self.pdf_splitter.clean(home_dir)
        return ParseResult(
            items=items,
            titles=titles
        )
