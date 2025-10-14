import os
import re
import tempfile

import urllib.parse


def is_local_path(path):
    return path.startswith('/')


def is_http_path(path):
    return urllib.parse.urlparse(path).scheme in ('http', 'https')


def get_temp_dir() -> str:
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, "pfip")


def get_file_name(file_path: str) -> str:
    """
    eg:
        in :  "./data/智能问答和智能搜索的区别有哪些？.txt"
        out: 智能问答和智能搜索的区别有哪些？.txt
    """
    file_name_with_ext = os.path.basename(file_path)
    return file_name_with_ext


def get_file_name_without_ext(file_path: str):
    """
    eg:
        in :  "./data/智能问答和智能搜索的区别有哪些？.txt"
        out: 智能问答和智能搜索的区别有哪些？
    """
    file_name_with_ext = os.path.basename(file_path)
    file_name, file_ext = os.path.splitext(file_name_with_ext)
    return file_name


def get_file_ext(file_path: str):
    file_name, file_ext = os.path.splitext(file_path)
    file_ext = file_ext[1:]
    return file_ext


def clean_file_name(file_name):
    # 使用正则表达式去除特殊符号，只保留数字、中文、英文和下划线
    cleaned_name = re.sub(r'[^\w\u4e00-\u9fa5]', '', file_name)  # \w 匹配字母、数字和下划线，\u4e00-\u9fa5 匹配中文字符
    return cleaned_name.strip()