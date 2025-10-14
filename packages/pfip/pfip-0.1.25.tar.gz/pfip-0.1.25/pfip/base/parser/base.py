import os
from abc import ABC, abstractmethod
from typing import List, Dict

from pydantic import BaseModel, ConfigDict

from pfip.base.errors import UnImplementException
from pfip.base.parser.parser_model import ParseResult, TitleNode
from pfip.base.util.file_util import get_temp_dir, clean_file_name


class Parser(ABC, BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    empty_line_pattern: str = r'^\s*$'
    full_title_max_len: int = 200

    @abstractmethod
    def support(self, file_ext: str) -> bool:
        return False

    @abstractmethod
    def __call__(self, file_path: str, **kwargs) -> ParseResult:
        raise UnImplementException("未实现...")

    @staticmethod
    def is_empty_line(line) -> bool:
        return len(line.strip()) == 0

    def fill_titles(self, titles: List[TitleNode]):
        """
            为 sn|pid 进行赋值
        """
        for idx, t in enumerate(titles):
            t.sn = idx + 1
        self.fill_title_pid(titles)
        self.fill_full_title(titles)

    @staticmethod
    def fill_title_pid(titles: List[TitleNode]):
        """
        根据title的前后关系以及level_type来进行确定
        """
        stack = []
        for i, title_node in enumerate(titles):
            while stack and stack[-1].title_level >= title_node.title_level:
                stack.pop()
            if stack:
                title_node.pid = stack[-1].id
            stack.append(title_node)

    def fill_full_title(self, nodes: List[TitleNode]):
        node_dict: Dict[str, TitleNode] = {node.id: node for node in nodes}
        for node in nodes:
            current = node
            full_title_list = []
            while current.pid is not None:
                parent = node_dict.get(current.pid)
                if parent:
                    full_title_list.insert(0, parent.title)
                    current = parent
            node.full_title = " - ".join(full_title_list + [node.title])
            if len(node.full_title) > self.full_title_max_len:
                # 如果full_title超过限制,则只是用首个节点的title
                node.full_title = nodes[0].title

    @staticmethod
    def get_home_dir(file_path: str):
        file_name_with_ext = os.path.basename(file_path)
        file_name, file_ext = os.path.splitext(file_name_with_ext)
        file_name = clean_file_name(file_name)
        file_ext = file_ext.replace(".", "")
        home_dir = os.path.join(get_temp_dir(), file_ext, file_name)
        if not os.path.exists(home_dir):
            os.makedirs(home_dir)
        return home_dir
