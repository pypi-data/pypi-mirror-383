import math
from typing import List, Optional

from loguru import logger
from panshi2task.embedding_client import EmbeddingTaskClient
from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self

from pfip.base.constant import TAtomItem
from pfip.base.parser.parser_model import TextAtomItem, TitleNode
from pfip.base.util.common import min_edit_distance


class TitleConnector(BaseModel):
    """
            便利title,从item中找寻最相似的候选集. 然后再通过语义相似度比较找到最终的1个.
            如果没找到: 则跳过即可
            如果找到: 则修改
             下次找的位置变换 :
                从
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    embedding_server_url: Optional[str] = None
    client: Optional[EmbeddingTaskClient] = None
    max_ld_radio: float = 0.5
    """最小编辑距离比率=编辑距离/max(字符串1长度+字符串2长度)"""
    min_score: float = 0.8

    @model_validator(mode='after')
    def init(self) -> Self:
        if self.embedding_server_url:
            self.client = EmbeddingTaskClient(self.embedding_server_url)
        else:
            logger.warning("embedding_server_url未设置,语义相似度功能将不可用...")
        return self


    def calculate_str2_max_length(self, str1_len: int) -> int:
        """
        在已知str1的长度以及比率时,得到str2的最大可能长度
        那么存在: len(str2) -5 / len(str1)+len(str2) = 0.3  也就是: len(str2) = 1.3*len(str1)/0.7
        """
        c1 = 1 + self.max_ld_radio
        c2 = 1 - self.max_ld_radio
        return math.ceil(c1 * str1_len / c2)


    def find_similar_title(self, title: TitleNode, candcates: List[tuple[TextAtomItem, int]]) -> int:
        """
            step1: 现根据title长度以及比率,获取TextAtomItem的最大可能长度,根据此长度过滤掉部分数据
            step2: 根据最小编辑距离,得到一批候选集
            step3: 根据语义相似度,返回最相似的一个
        """
        failed_result = -1
        item_max_len = self.calculate_str2_max_length(len(title.title))
        candcates1 = [item for item in candcates if item[0].item_type in [TAtomItem.TITLE, TAtomItem.TEXT]]
        candcates2 = [item for item in candcates1 if len(item[0].content) <= item_max_len]
        candcates3 = []
        for item, idx in candcates2:
            max_len = max(len(title.title), len(item.content))
            radio = min_edit_distance(title.title, item.content) / max_len
            if radio <= self.max_ld_radio:
                candcates3.append((item, idx, radio))

        if not candcates3:
            return failed_result
        if self.client:
            texts = [c[0].content for c in candcates3]
            most_similar_text, score = self.client.text_similar(title.title, texts)
            if score > self.min_score:
                return [c[1] for c in candcates3 if c[0].content == most_similar_text][0]
            else:
                return failed_result
        else:
            min_tuple = min(candcates3, key=lambda tuple_item: tuple_item[2])
            return min_tuple[1]
