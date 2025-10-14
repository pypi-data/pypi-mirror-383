import re
from abc import ABC, abstractmethod
from collections import deque
from typing import List

import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel

from pfip.base.errors import UnImplementException
from pfip.base.parser.parser_model import AtomItem, TitleAtomItem, TextAtomItem, TableAtomItem, MDListAtomItem, \
    MDCodeAtomItem, MDRefAtomItem, MDHtmlAtomItem


class MDElementHandler(ABC, BaseModel):
    @abstractmethod
    def support(self, line: str) -> bool:
        raise UnImplementException()

    @abstractmethod
    def run(self, start_line: str, q: deque[str]) -> AtomItem:
        raise UnImplementException()


class MDParagraphHandler(MDElementHandler):
    def support(self, line: str) -> bool:
        return True

    def run(self, start_line: str, q: deque[str]) -> TextAtomItem:
        return TextAtomItem.instance(start_line)


class MDTitleHandler(MDElementHandler):
    reg: str = r'^(#+)\s+(.*)$'

    def support(self, line: str) -> bool:
        return bool(re.match(self.reg, line))

    def run(self, start_line: str, q: deque[str]) -> TitleAtomItem:
        match = re.match(self.reg, start_line)
        level = len(match.group(1))
        title = match.group(2)
        return TitleAtomItem.instance(title, level)


class MDTableHandler(MDElementHandler):
    reg: str = r'^\|\s*(.*?)\s*\|\s*(.*?)\s*\|$'

    def support(self, line: str) -> bool:
        return bool(re.match(self.reg, line))

    @staticmethod
    def mdtable2df(lines: List[str]) -> DataFrame:
        header = [h.strip() for h in re.split(r'\s*\|\s*', lines[0]) if h.strip()]
        data = [[d.strip() for d in re.split(r'\s*\|\s*', line) if d.strip()] for line in lines[2:]]
        return pd.DataFrame(data, columns=header)

    def run(self, start_line: str, q: deque[str]) -> TableAtomItem:
        table_lines = [start_line]
        while q:
            line = q.popleft()
            if bool(re.match(self.reg, line)):
                table_lines.append(line)
            else:
                q.appendleft(line)
                break
        df = self.mdtable2df(table_lines)
        return TableAtomItem.simple(df=df)


class MDListHandler(MDElementHandler):
    unordered_list_reg: str = r'^[\*\-\+] .*'
    ordered_list_reg: str = r'^\d+\. .*'

    def support(self, line: str) -> bool:
        return bool(re.match(self.unordered_list_reg, line)) or bool(re.match(self.ordered_list_reg, line))

    def run(self, start_line: str, q: deque[str]) -> MDListAtomItem:
        list_lines = [start_line]
        while q:
            line = q.popleft()
            if self.support(line):
                list_lines.append(line)
            else:
                q.appendleft(line)
                break
        return MDListAtomItem.simple(content=list_lines)


class MDCodeHandler(MDElementHandler):
    def support(self, line: str):
        return line.startswith("```")

    def run(self, start_line: str, q: deque[str]) -> MDCodeAtomItem:
        code_lines = [start_line]
        while q:
            line = q.popleft()
            if line == "```":
                break
            else:
                code_lines.append(line)
        language = start_line.replace("```", "")
        return MDCodeAtomItem.simple(content=code_lines, language=language)


class MDRefHandler(MDElementHandler):
    def support(self, line: str):
        return line.startswith(">")

    def run(self, start_line: str, q: deque[str]) -> MDRefAtomItem:
        ref_lines = [start_line]
        while q:
            line = q.popleft()
            if line.startswith(">"):
                ref_lines.append(line)
            else:
                q.appendleft(line)
                break
        return MDRefAtomItem.simple(content=ref_lines)


class MdHtmlHandler(MDElementHandler):
    html_start_pattern: str = r'<(\w+)\s+[^>/]*>'
    """<div xxx>"""
    html_pattern: str = r'<(\w+)\s+[^>]*>.*?</\1>'
    """ <div> xxx </div>"""
    single_line_html_pattern: str = r'<(\w+)\s+[^>]*/>'
    """ <div xxx/>"""

    def support(self, line: str):
        match1 = re.fullmatch(self.html_start_pattern, line.strip(), re.DOTALL)
        match2 = re.fullmatch(self.single_line_html_pattern, line.strip(), re.DOTALL)
        match3 = re.fullmatch(self.html_pattern, line.strip(), re.DOTALL)
        return match1 or match2 or match3


    def run(self, start_line: str, q: deque[str]) -> MDHtmlAtomItem:
        single_match = re.fullmatch(self.single_line_html_pattern, start_line.strip(), re.DOTALL)
        single_match2 = re.fullmatch(self.html_pattern, start_line.strip(), re.DOTALL)
        if single_match or single_match2:
            return MDHtmlAtomItem.simple(content=[start_line])
        else:
            html_lines = [start_line]
            while q:
                html_content = "".join(html_lines)
                match = re.fullmatch(self.html_pattern, html_content.strip(), re.DOTALL)
                if match:
                    break
                else:
                    line = q.popleft()
                    html_lines.append(line)
            return MDHtmlAtomItem.simple(content=html_lines)
