import os
import shutil
from typing import List

from loguru import logger
from pydantic import BaseModel
from PyPDF2 import PdfReader, PdfWriter

from pfip.base.util.file_util import get_file_name_without_ext


class PdfSplitter(BaseModel):
    max_split_pdf_num: int = 10
    split_pdf_dir: str = "splits"

    @staticmethod
    def get_split_pdf_name(start_page: int, end_page: int) -> str:
        return f"split_{start_page}_{end_page}.pdf"

    @staticmethod
    def get_page_area_from_name(file_path: str) -> tuple[int, int]:
        file_name = get_file_name_without_ext(file_path)
        if file_name.startswith("split_"):
            file_name = file_name.replace("split_", "")
            start_page = file_name.split("_")[0]
            end_page = file_name.split("_")[1]
            return int(start_page), int(end_page)
        else:
            return 0, 0

    def clean(self, home_dir: str):
        output_dir = os.path.join(home_dir, self.split_pdf_dir)
        if os.path.exists(output_dir):
            try:
                shutil.rmtree(output_dir)
            except OSError as e:
                logger.error(f"Error: {e.strerror}")

    def split(self, file_path: str, home_dir: str) -> List[str]:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)

        if total_pages < self.max_split_pdf_num:
            """不需要切分,直接返回"""
            return [file_path]

        output_dir = os.path.join(home_dir, self.split_pdf_dir)
        os.makedirs(output_dir, exist_ok=True)

        start_page = 0
        split_index = 1
        all_split_paths = []
        while start_page < total_pages:
            writer = PdfWriter()
            end_page = min(start_page + self.max_split_pdf_num, total_pages)
            split_file_name = self.get_split_pdf_name(start_page, end_page)
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            output_file = os.path.join(output_dir, split_file_name)
            with open(output_file, 'wb') as output_pdf:
                writer.write(output_pdf)
            start_page = end_page
            split_index += 1
            all_split_paths.append(output_file)
        return all_split_paths
