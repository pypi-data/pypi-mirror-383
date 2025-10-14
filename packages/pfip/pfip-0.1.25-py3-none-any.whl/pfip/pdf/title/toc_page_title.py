import re
from abc import ABC, abstractmethod
from typing import List, Any, Tuple

from pydantic import BaseModel, Field, model_validator

from pfip.base.constant import TAtomItem
from pfip.base.parser.parser_model import TitleNode, AtomItem
from pfip.base.util.kangxi2chinese import TxtCleaner
from pfip.pdf.title.base import TitleExtractor


class PageItem(BaseModel):
    num: int
    lines: List[str]


class TocRule(ABC):
    @abstractmethod
    def is_toc(self, page: PageItem) -> bool:
        pass


class TocRule1(TocRule):
    min_scale: float = 0.7

    def is_toc(self, page: PageItem) -> bool:
        if len(page.lines) == 0:
            return False
        toc_line_num = 0
        pattern = re.compile(r'^[0-9].*')
        for l in page.lines:
            if re.match(pattern, l):
                toc_line_num += 1
        scale = toc_line_num / len(page.lines)
        return scale >= self.min_scale


class TocPageJudge:
    """
    管理Rule,判定输入页码是否为目录页
    """

    def __init__(self):
        self.rules: List[TocRule] = [TocRule1()]

    def judge(self, page: PageItem) -> bool:
        for rule in self.rules:
            if rule.is_toc(page):
                return True
        return False


class DetectTocPagesHandler(BaseModel):
    """
        用于检测目录所在页码
    """
    max_check_page_num: int

    def remove_chars(self, s: str) -> str:
        # 移除每个字符串中的所有非数字、汉字和英文字母
        s0 = TxtCleaner().aswhole(s)
        pattern = re.compile(r'[^\w\d\u4e00-\u9fa5]')
        s1 = pattern.sub('', s0)
        s2 = s1.removeprefix("第")
        s3 = self.replace_chinese_number_prefix(s2)
        s4 = self.roman_to_int(s3)
        return s4

    @staticmethod
    def roman_to_int(input_str):
        roman_dict = {'I': "1", 'V': "5", 'X': "10"}

        # 使用正则表达式匹配字符串中的罗马数字部分
        pattern = re.compile(r'^[IVX]+', re.IGNORECASE)
        match = pattern.match(input_str)
        if match:
            roman_numeral = match.group()
            for char in roman_numeral:
                if char.upper() in roman_dict:
                    input_str = input_str.replace(char, roman_dict[char.upper()], 1)  # 将汉字数字替换为阿拉伯数字，只替换一次
        return input_str

    def page_deal(self, ps: List[PageItem]) -> List[PageItem]:
        dealed = []
        for p in ps:
            dl = []
            for l in p.lines:
                line = self.remove_chars(l)
                if len(line) > 0:
                    dl.append(self.remove_chars(l))
            dealed.append(PageItem(num=p.num, lines=dl))
        return dealed

    @staticmethod
    def group_consecutive_numbers(nums):
        """
        获取最大的连贯分组
        :param nums:
        :return:
        """
        nums.sort()
        groups = []
        current_group = [nums[0]]

        for i in range(1, len(nums)):
            if nums[i] - nums[i - 1] == 1:
                current_group.append(nums[i])
            else:
                groups.append(current_group)
                current_group = [nums[i]]

        groups.append(current_group)

        max_group = max(groups, key=len)

        return max_group

    @staticmethod
    def replace_chinese_number_prefix(input_str):
        chinese_nums = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8',
                        '九': '9',
                        '十': '10'}
        pattern = "^[" + "".join(chinese_nums.keys()) + "]+"

        match = re.match(pattern, input_str)
        if match:
            chinese_prefix = match.group()
            for char in chinese_prefix:
                if char in chinese_nums:
                    input_str = input_str.replace(char, chinese_nums[char], 1)  # 将汉字数字替换为阿拉伯数字，只替换一次
        return input_str

    def load(self, text_items: List[AtomItem]) -> List[PageItem]:
        _pages = []
        max_page_num = min(self.max_check_page_num, text_items[-1].start_page)
        for page_idx in range(max_page_num):
            page_num = page_idx + 1
            lines = [item.content for item in text_items if item.start_page == page_num]
            _pages.append(PageItem(num=page_num, lines=lines))
        return _pages

    def __call__(self, text_items: List[AtomItem]) -> List[int]:
        pages = self.load(text_items)
        # 预处理
        dealed_pages = self.page_deal(pages)
        page_judge = TocPageJudge()
        toc_pages = []
        for dp in dealed_pages:
            if page_judge.judge(dp):
                toc_pages.append(dp)

        if len(toc_pages) == 0:
            return []
        # 确定最终的目录页
        num_list = [item.num for item in toc_pages]
        g1 = self.group_consecutive_numbers(num_list)
        final_pages = [item.num for item in toc_pages if item.num in g1]
        return final_pages


class TocPageTitleExtractor(TitleExtractor):
    handler: DetectTocPagesHandler = Field(exclude=True)

    @model_validator(mode='before')
    def init(cls, data: Any) -> Any:
        if "max_check_page_num" in data and isinstance(data["max_check_page_num"], int):
            max_check_page_num = data["max_check_page_num"]
        else:
            max_check_page_num = 10
        data["handler"] = DetectTocPagesHandler(max_check_page_num=max_check_page_num)
        return data

    @staticmethod
    def _load(items: List[AtomItem], toc_page_numbers: List[int]):
        result = []
        for item in items:
            if item.start_page in toc_page_numbers:
                result.append(item)
        return result

    @staticmethod
    def is_filter(item: AtomItem) -> bool:
        if item.content.upper() in ["目录", "TABLEOFCONTENTS", "CONTENTS"]:
            return True
        else:
            return False

    def extract_title_content(self, catalog_title: str) -> str:
        title = None
        for extract_rule in self.extract_rules:
            data = extract_rule.extract(catalog_title)
            if data:
                title = data[0]
                break
        return title

    @staticmethod
    def define_level_type_by_indent(title_with_indents: List[Tuple[str, float]]) -> List[Tuple[str, int]]:
        """根据缩进距离,确定级别大小"""
        if title_with_indents:
            indents = [ti[1] for ti in title_with_indents]
            unique_indents = list(set(indents))
            sorted_unique_indents = sorted(unique_indents)
            differences = [j - i for i, j in zip(sorted_unique_indents[:-1], sorted_unique_indents[1:])]
            # 初始化分组列表
            groups = []
            group = [sorted_unique_indents[0]]
            # 根据差值分组
            for i, diff in enumerate(differences):
                if diff > 5:
                    groups.append(group)
                    group = [sorted_unique_indents[i + 1]]
                else:
                    group.append(sorted_unique_indents[i + 1])
            groups.append(group)
            result_dict = {}
            for idx, group in enumerate(groups):
                for element in group:
                    result_dict[element] = idx + 1
            return [(ti[0], result_dict[ti[1]]) for ti in title_with_indents]
        else:
            return []

    @staticmethod
    def deal_titles(title_with_indents: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """
            处理TITLE
            1. 去除异常title
            2. 提取title信息
        """
        rtn = []
        # 去除异常title
        need_remove_idx = []
        error_title_pattern1 = r'^[\d.]+$'
        for idx, ti in enumerate(title_with_indents):
            if re.match(error_title_pattern1, ti[0]):
                need_remove_idx.append(idx)
        # 提取title信息
        for idx, ti in enumerate(title_with_indents):
            if idx in need_remove_idx:
                continue
            # 省略号格式: '法律声明.............I'
            match1 = re.search(r'(.*?)\.{3,}(.*)', ti[0])
            if match1:
                rtn.append((match1.groups()[0], ti[1]))
                continue
            rtn.append(ti)
        return rtn

    def __call__(self, pdf_path: str, items: List[AtomItem]) -> List[TitleNode]:
        """
        1) 确定级别
        2) 上下级关系构建
        3) page_number 不需要
        """
        text_items = [item for item in items if item.item_type == TAtomItem.TEXT]
        if not text_items:
            return []
        toc_page_numbers = self.handler(text_items)
        if not toc_page_numbers:
            return []
        multi_page_items = self._load(text_items, toc_page_numbers)
        title_with_indents = []
        for item in multi_page_items:
            if self.is_filter(item):
                continue
            title_with_indents.append((item.content, item.location.x0))
        dealed_title_with_indents = self.deal_titles(title_with_indents)
        title_with_lv = self.define_level_type_by_indent(dealed_title_with_indents)
        title_nodes = []
        for idx, tlv in enumerate(title_with_lv):
            td = TitleNode(
                title=re.sub(r'\s+', '', tlv[0]),
                title_level=tlv[1],
                sn=idx + 1
            )
            title_nodes.append(td)
        return title_nodes
