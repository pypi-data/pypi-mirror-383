import re

from pfip.base.util.kangxi2chinese import TxtCleaner

TXT_CLEANER = TxtCleaner()


def remove_whitespace(text: str, except_newline: bool = False):
    """使用正则表达式去除所有空格和不可见字符"""
    if except_newline:
        return re.sub(r'[^\S\n]+', '', text)
    else:
        return re.sub(r'\s+', '', text)


def clean_str(content: str, except_newline: bool = False) -> str:
    if content:
        content = TXT_CLEANER.aswhole(content)
        content = remove_whitespace(content, except_newline)
        return content
    else:
        return content


def clean_str_keep_spaces(content: str) -> str:
    if content:
        content = TXT_CLEANER.aswhole(content)
        content = re.sub(r'[\t\n\r]', '', content)
        return content
    else:
        return content


def remove_empty_lines(lines: list):
    """移除列表中的空行和只包含空白字符的行"""
    return list(filter(lambda line: line.strip(), lines))
