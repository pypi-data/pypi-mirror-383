import re
from typing import List, Any, Optional

from bs4 import BeautifulSoup
from pandas import DataFrame
from pydantic import BaseModel, Field, ConfigDict, computed_field

from pfip.base.constant import TAtomItem, ROOT_TITLE_LEVEL
from pfip.base.util.file_util import get_file_name_without_ext
from pfip.base.util.generator_id import id_generator


# ==================标题===============
class TitleNode(BaseModel):
    """文档标题节点"""
    id: str = Field(default_factory=lambda: str(id_generator.next_id()))
    title: str
    title_level: int
    full_title: str = None
    """ 基于上级的标题+自身的拼接而成 """
    pid: str | None = None
    page_number: int | None = None
    sn: int = 0


# ==================文档内容===============
class Location(BaseModel):
    """左侧与页面左侧的距离。"""
    x0: Optional[float] = None
    """右侧与页面左侧的距离。"""
    x1: Optional[float] = None
    """下方与页面底部的距离。"""
    y0: Optional[float] = None
    """页面顶部末端的距离。"""
    y1: Optional[float] = None


class AtomItem(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """原子文档内容项"""
    item_type: TAtomItem
    content: Any
    start_page: int
    end_page: int
    location: Optional[Location] = None

    @computed_field
    def full_content(self) -> str:
        raise ""


class TextAtomItem(AtomItem):
    """普通的文本项"""
    item_type: TAtomItem = TAtomItem.TEXT
    content: str

    @classmethod
    def instance(cls, content: str, page_num: int = 1) -> "TextAtomItem":
        return cls(content=content, start_page=page_num, end_page=page_num)

    @computed_field
    def full_content(self) -> str:
        return self.content


class WordTextAtomItem(TextAtomItem):
    auto_num: str = Field(default="", description="自动编号")

    @computed_field
    def without_auto_num_content(self) -> str:
        """
        不包含自动页码的content
        """
        return self.content.replace(self.auto_num, "")


class ImageAtomItem(AtomItem):
    """图片"""
    item_type: TAtomItem = TAtomItem.IMAGE
    content: str | None
    image_url: str

    @classmethod
    def simple(cls, image_url: str, content: str | None = None, page_num: int = 1) -> "ImageAtomItem":
        return cls(image_url=image_url, content=content, start_page=page_num, end_page=page_num)

    @computed_field
    def full_content(self) -> str:
        desc = self.content or "没有描述"
        return f"![{desc}]({self.image_url})"


class ImageCaptionAtomItem(AtomItem):
    """图片描述信息 目前仅版面分析模型支持"""
    item_type: TAtomItem = TAtomItem.IMAGE_CAPTION
    content: str

    @classmethod
    def simple(cls, content: str, page_num: int = 1) -> "ImageCaptionAtomItem":
        return cls(content=content, start_page=page_num, end_page=page_num)

    @computed_field
    def full_content(self) -> str:
        return self.content


class TableAtomItem(AtomItem):
    """表格"""
    item_type: TAtomItem = TAtomItem.TABLE
    content: Optional[str] = Field(default=None, description="表格描述信息")
    df: DataFrame = Field(exclude=True)

    @classmethod
    def simple(cls, df: DataFrame, desc: str = None, page_num: int = 1) -> "TableAtomItem":
        return cls(df=df, content=desc, start_page=page_num, end_page=page_num)

    @computed_field
    def table_desc(self) -> str:
        header = self.df.columns.tolist()
        dealed_header = [re.sub(r'\s+', '', str(h)) for h in header if h and str(h).strip()]
        desc = '|'.join(dealed_header)
        if self.content:
            desc = f"{self.content},表头信息:{desc}"
        return desc

    @computed_field
    def full_content(self) -> str:
        html_table = self.df.to_html(justify="center")
        if self.content:
            soup = BeautifulSoup(html_table, 'html.parser')
            caption = soup.new_tag('caption')
            caption.string = self.content
            table = soup.find('table')
            table.insert(0, caption)
            html_table = table.prettify()
        return html_table


class ScannedPDFTableAtomItem(AtomItem):
    """表格"""
    item_type: TAtomItem = TAtomItem.TABLE
    content: Optional[str] = Field(default=None, description="表格描述信息")
    table_html: str

    @classmethod
    def simple(cls, table_html: str, desc: str = None, page_num: int = 1) -> "ScannedPDFTableAtomItem":
        return cls(table_html=table_html, content=desc, start_page=page_num, end_page=page_num)

    @computed_field
    def table_desc(self) -> str:
        soup = BeautifulSoup(self.table_html, 'html.parser')
        rows = soup.find_all(["th", 'tr'])
        header = [data.text for data in rows[0].find_all('td')]
        dealed_header = [re.sub(r'\s+', '', h) for h in header if h and str(h).strip()]
        desc = '|'.join(dealed_header)
        if self.content:
            desc = f"{self.content},表头信息:{desc}"
        return desc

    @computed_field
    def full_content(self) -> str:
        html_table = self.table_html
        if self.content:
            soup = BeautifulSoup(html_table, 'html.parser')
            caption = soup.new_tag('caption')
            caption.string = self.content
            table = soup.find('table')
            table.insert(0, caption)
            html_table = table.prettify()
        return html_table


class TextPDFTableAtomItem(TableAtomItem):
    """表格"""
    page_height: float = Field(default=0.0, exclude=True)
    replace_items: List[TextAtomItem] = Field(default=[], exclude=True)
    """对应的重复文本item"""

    @classmethod
    def simple(cls, df: DataFrame, page_height: float, desc: str = None, page_num: int = 1) -> "TextPDFTableAtomItem":
        return cls(content=desc, df=df, page_height=page_height, start_page=page_num, end_page=page_num)


class TitleAtomItem(TextAtomItem):
    """标题"""
    item_type: TAtomItem = TAtomItem.TITLE
    content: str
    title_level: int
    title_node: Optional[TitleNode] = Field(default=None, exclude=True)

    @classmethod
    def instance(cls, content: str, title_level: int, page_num: int = 1) -> "TitleAtomItem":
        return cls(content=content, title_level=title_level, start_page=page_num, end_page=page_num)

    @classmethod
    def from_file(cls, file_path: str, mkpos: bool = False) -> "TitleAtomItem":
        title = get_file_name_without_ext(file_path)
        item = cls(
            content=title,
            title_level=ROOT_TITLE_LEVEL,
            start_page=1,
            end_page=1
        )
        if mkpos:
            location = Location(x0=0.0, x1=0.0, y0=0.0, y1=0.0)
            item.location = location
        return item

    def create_and_connect(self) -> TitleNode:
        """
        基于TitleAtomItem生成标题节点并与自身关联
        """
        tn = TitleNode(
            title=self.content,
            page_number=self.start_page,
            title_level=self.title_level
        )
        self.title_node = tn
        return tn


class WordTitleAtomItem(TitleAtomItem):
    auto_num: str = Field(default="", description="自动编号")

    @computed_field
    def without_auto_num_content(self) -> str:
        """
        不包含自动页码的content
        """
        return self.content.replace(self.auto_num, "")


class MDListAtomItem(AtomItem):
    item_type: TAtomItem = TAtomItem.MD_LIST
    content: List[str]

    @classmethod
    def simple(cls, content: List[str]) -> "MDListAtomItem":
        return cls(content=content, start_page=1, end_page=1)

    @computed_field
    def full_content(self) -> str:
        return "\n".join(self.content)


class MDCodeAtomItem(AtomItem):
    item_type: TAtomItem = TAtomItem.MD_CODE
    content: List[str]
    language: str

    @classmethod
    def simple(cls, content: List[str], language: str) -> "MDCodeAtomItem":
        return cls(content=content, language=language, start_page=1, end_page=1)

    @computed_field
    def full_content(self) -> str:
        return "\n".join(self.content)


class MDRefAtomItem(AtomItem):
    item_type: TAtomItem = TAtomItem.MD_REF
    content: List[str]

    @classmethod
    def simple(cls, content: List[str]) -> "MDRefAtomItem":
        return cls(content=content, start_page=1, end_page=1)

    @computed_field
    def full_content(self) -> str:
        return "\n".join(self.content)


class MDHtmlAtomItem(AtomItem):
    item_type: TAtomItem = TAtomItem.MD_HTML
    content: List[str]

    @classmethod
    def simple(cls, content: List[str]) -> "MDHtmlAtomItem":
        return cls(content=content, start_page=1, end_page=1)

    @computed_field
    def full_content(self) -> str:
        return "\n".join(self.content)


class AtomItemList(BaseModel):
    items: List[AtomItem]

    @computed_field
    def images(self) -> List[ImageAtomItem]:
        return [item for item in self.items if item.item_type == TAtomItem.IMAGE]

    @computed_field
    def titles(self) -> List[TitleAtomItem]:
        return [item for item in self.items if item.item_type == TAtomItem.TITLE]

    @computed_field
    def tables(self) -> List[TableAtomItem]:
        return [item for item in self.items if item.item_type == TAtomItem.TABLE]

    @computed_field
    def texts(self) -> List[TextAtomItem]:
        return [item for item in self.items if item.item_type == TAtomItem.TEXT]


class ParseResult(BaseModel):
    titles: List[TitleNode] = []
    items: List[AtomItem] = []

    @computed_field()
    def content(self) -> str:
        item_contents = [item.full_content for item in self.items]
        return "\n".join(item_contents)
