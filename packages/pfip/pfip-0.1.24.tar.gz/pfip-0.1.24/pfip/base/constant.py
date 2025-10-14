from enum import Enum


ROOT_TITLE_LEVEL = 0
UNKOWN_TITLE_LEVEL = 100

CONVERTED_PDF_PATH_KEY = "converted_pdf_path"
JSON_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8"
}

TABLE_FILL_HEADER_PREIX = "fill_header_"


class TChunk(str, Enum):
    IMAGE = "image"
    TABLE = "table"
    TEXT = "text"


class TSentence(str, Enum):
    IMAGE = "image"
    TABLE = "table"
    TEXT = "text"


class TPdf(str, Enum):
    TEXT = "text"
    SCANNED = "scanned"


class TAtomItem(str, Enum):
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    IMAGE_CAPTION = "image_caption"
    TITLE = "title"
    MD_REF = "md_ref"
    MD_CODE = "md_code"
    MD_LIST = "md_list"
    MD_HTML = "md_html"


class TFileExt(str, Enum):
    MD = "md"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    PDF = "pdf"
    HTML = "html"
    XLS = "xls"
    XLSX = "xlsx"
    PPT = "ppt"
    PPTX = "pptx"
