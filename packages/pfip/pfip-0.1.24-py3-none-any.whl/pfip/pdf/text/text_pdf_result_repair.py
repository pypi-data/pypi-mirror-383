import itertools
from collections import defaultdict, Counter
from typing import List, Dict

import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel, model_validator
from typing_extensions import Self

from pfip.base.constant import TAtomItem
from pfip.base.parser.parser_model import AtomItem, TableAtomItem, ImageAtomItem, TitleNode, TitleAtomItem, \
    TextPDFTableAtomItem
from pfip.base.parser.repair import TableDescRepair, ImageDescRepair
from pfip.base.util.rectangle import RectangleHelper
from pfip.pdf.title.title_item_connector import TitleConnector


class CrossPageTableRepair(BaseModel):
    """
        跨页表格发现及合并处理
    """

    @staticmethod
    def _merge_cross_page_tables(merge_table_idxs: List[int], items: List[AtomItem]):
        """
        合并表格
        :param merge_table_idxs:
        :param items:
        :return:
        """
        first_part_table: TextPDFTableAtomItem = items[merge_table_idxs[0]]
        first_header = first_part_table.df.columns.tolist()
        first_rows = first_part_table.df.values.tolist()
        replace_items = first_part_table.replace_items
        end_page = items[merge_table_idxs[-1]].end_page
        for idx in merge_table_idxs[1:]:
            header = items[idx].df.columns.tolist()
            rows = items[idx].df.values.tolist()
            if header != first_header:
                first_rows.append(header)
            first_rows.extend(rows)
            replace_items.extend(items[idx].replace_items)
        df = pd.DataFrame(first_rows, columns=first_header)
        items[merge_table_idxs[0]].df = df
        items[merge_table_idxs[0]].end_page = end_page

    @staticmethod
    def _is_top_start_table(table_item: AtomItem) -> bool:
        """
        判断表格是否是当前页顶部起始的表格
        :param table_item:
        :return:
        """
        if table_item.location.y1 / table_item.page_height > 0.9:
            return True
        return False

    @staticmethod
    def _is_adjoin_page_table(pre_table_item: AtomItem, current_table_item: AtomItem) -> bool:
        """
        判断是否是相邻页的两个表格
        :param pre_table_item:
        :param current_table_item:
        :return:
        """
        if pre_table_item.end_page + 1 == current_table_item.start_page:
            return True
        return False

    @staticmethod
    def _is_same_width_table(pre_table_item: AtomItem, current_table_item: AtomItem) -> bool:
        """
        判断表格宽度是否相同
        宽度误差在5以内都算相同
        :param pre_table_item:
        :param current_table_item:
        :return:
        """
        pre_table_width = pre_table_item.location.x1 - pre_table_item.location.x0
        current_table_width = current_table_item.location.x1 - current_table_item.location.x0
        return abs(pre_table_width - current_table_width) < 5

    def _is_cross_page_table(self, pre_table_item: AtomItem, current_table_item: AtomItem) -> bool:
        """
        判断前一个表格和当前表格是否是跨页的
        判断逻辑：
        1.当相邻两个表格header不同，但列数相同、表宽相同、页码相邻、header位置在页面顶部时，满足这些条件表示当前表格与上一个表格是跨页表格。
        2.相邻两个表格header相同、位置在页面顶部时,也是跨页表格。
        :param pre_table_item:
        :param current_table_item:
        :return:
        """
        pre_table_headers = pre_table_item.df.columns.tolist()
        current_table_headers = current_table_item.df.columns.tolist()
        # 是否是相同列数
        is_same_columns_count = len(pre_table_headers) == len(current_table_headers)
        # 是否是相邻页
        is_adjoin_page = self._is_adjoin_page_table(pre_table_item, current_table_item)
        # 是否相同宽度
        is_same_width = self._is_same_width_table(pre_table_item, current_table_item)
        # 是否是顶部起始
        is_top = self._is_top_start_table(current_table_item)
        if pre_table_headers == current_table_headers:
            if is_top and is_adjoin_page:
                return True
        else:
            if is_same_columns_count and is_adjoin_page and is_same_width:
                return True
        return False

    def run(self, items: List[AtomItem]) -> List[AtomItem]:
        """
        跨页表格处理
        逻辑：
          1.大于1个表格数才会考虑跨页合并问题
          2.先判断当前表格与前一个表格是否是跨页的,如果是，将索引位置添加到列表中，列表第一个元素为表格开始部分，剩余为待合并部分。
          3.合并完，将待合并部分的元素从列表中移除。
        :param items:
        :return:
        """
        table_item_idxs = []
        for idx, item in enumerate(items):
            if item.item_type == TAtomItem.TABLE:
                table_item_idxs.append(idx)
        if len(table_item_idxs) > 1:
            merge_table_idxs = []
            removed_idx = []
            for i, idx in enumerate(table_item_idxs[1:], start=1):
                if self._is_cross_page_table(items[table_item_idxs[i - 1]], items[idx]):
                    if merge_table_idxs:
                        merge_table_idxs.append(idx)
                        removed_idx.append(idx)
                    else:
                        merge_table_idxs = [table_item_idxs[i - 1], idx]
                        removed_idx.append(idx)
                else:
                    if merge_table_idxs:
                        self._merge_cross_page_tables(merge_table_idxs, items)
                        merge_table_idxs = []
            items = [item for index, item in enumerate(items) if index not in removed_idx]
        return items


class TableRectAngleContainer(BaseModel):
    table_idx: int
    table_item: TextPDFTableAtomItem
    indexs: List[int] = []
    rectangle_helper: RectangleHelper = None
    """连续的值"""

    @model_validator(mode="after")
    def init(self) -> Self:
        location = self.table_item.location
        self.rectangle_helper = RectangleHelper(
            bottom_left=(location.x0, location.y0), top_right=(location.x1, location.y1)
        )

    def get_sort_val(self) -> int:
        if self.indexs:
            return self.indexs[0]
        else:
            return 10000

    def is_empty(self) -> bool:
        return len(self.indexs) == 0

    def is_table_contained(self, idx: int, item: AtomItem) -> bool:
        x1, y1 = item.location.x0, item.location.y0
        x2, y2 = item.location.x1, item.location.y1

        self.rectangle_helper.contains((x1, y1), (x2, y2))
        if self.rectangle_helper.contains((x1, y1), (x2, y2)):
            self.indexs.append(idx)
            return True
        else:
            return False


class ImagePosRepair(BaseModel):
    @staticmethod
    def change_img_pos(items: List[AtomItem]) -> List[AtomItem]:
        not_image_items = [(idx, item) for idx, item in enumerate(items) if item.item_type != TAtomItem.IMAGE]
        image_items = [(idx, item) for idx, item in enumerate(items) if item.item_type == TAtomItem.IMAGE]
        changed_images_pos = []
        changed_images_ori_index = []
        for image_idx, image in image_items:
            l0 = image.location
            helper = RectangleHelper(bottom_left=(l0.x0, l0.y0), top_right=(l0.x1, l0.y1))
            for item_with_idx1, item_with_idx2 in zip(not_image_items[:-1], not_image_items[1:]):
                idx1, item1 = item_with_idx1[0], item_with_idx1[1]
                idx2, item2 = item_with_idx2[0], item_with_idx2[1]
                l1 = item1.location
                l2 = item2.location
                flag1 = not helper.in_top((l1.x0, l1.y0), (l1.x1, l1.y1))
                flag2 = helper.in_top((l2.x0, l2.y0), (l2.x1, l2.y1))
                if flag1 and flag2:
                    changed_images_pos.append(idx1)
                    changed_images_ori_index.append(image_idx)
                    break
        rtn = []
        for idx, item in enumerate(items):
            if idx in changed_images_pos:
                rtn.append(item)
                image_item = image_items[changed_images_pos.index(idx)]
                rtn.append(image_item[1])
            elif idx in changed_images_ori_index:
                continue
            else:
                rtn.append(item)
        return rtn

    def is_whole_page_image(self, image: ImageAtomItem) -> bool:
        """
        判断是否是整页的图片
        x0、y0 与 0 的误差在5之内
        :param image:
        :return:
        """
        if abs(image.location.x0 - 0) < 5 and abs(image.location.y0 - 0) < 5:
            return True
        return False

    def get_watermark_indexs(self, images: List[tuple[int, ImageAtomItem]]) -> List[int]:
        """
            localtion完全一致image>3,则被认为是水印
            额外再判断是否是整页的location，如果是，排除掉水印的可能
        """
        location_counts = defaultdict(int)
        watermark_indexs = []
        water_mark_image_locations = []
        for _, image in images:
            if not self.is_whole_page_image(image):
                location_key = (image.location.x0, image.location.x1, image.location.y0, image.location.y1)
                location_counts[location_key] += 1
        for location, count in location_counts.items():
            if count > 2:
                water_mark_image_locations.append(location)
        for idx, image in images:
            location_key = (image.location.x0, image.location.x1, image.location.y0, image.location.y1)
            if location_key in water_mark_image_locations:
                watermark_indexs.append(idx)
        return watermark_indexs

    def run(self, items: List[AtomItem]) -> List[AtomItem]:
        rtn = []
        images_with_idx: List[tuple[int, ImageAtomItem]] = []
        for idx, item in enumerate(items):
            if item.item_type == TAtomItem.IMAGE:
                images_with_idx.append((idx, item))
        # 去除水印
        watermark_indexs = self.get_watermark_indexs(images_with_idx)
        remove_watermark_items = [item for idx, item in enumerate(items) if idx not in watermark_indexs]
        # 改变图片坐标位置
        page_grouped_items = []
        for _, group in itertools.groupby(remove_watermark_items, key=lambda x: x.start_page):
            page_grouped_items.append(list(group))
        for group in page_grouped_items:
            image_dealed_group = self.change_img_pos(group)
            rtn.extend(image_dealed_group)
        return rtn


class TablePosRepair(BaseModel):
    """
        调整表格图片的位置,插入到正确的Item前后; 并移除表格图片对应的TextAtomItem
    """

    @staticmethod
    def deal_table(page_items: List[AtomItem]) -> List[AtomItem]:
        not_table_items = [(idx, item) for idx, item in enumerate(page_items) if item.item_type != TAtomItem.TABLE]
        table_items = [(idx, item) for idx, item in enumerate(page_items) if item.item_type == TAtomItem.TABLE]
        table_containers = []
        for table_idx, table in table_items:
            container = TableRectAngleContainer(table_idx=table_idx, table_item=table)
            for idx, item in not_table_items:
                in_container = container.is_table_contained(idx, item)
                if not in_container and not container.is_empty():
                    """当container中已经有了元素,并且遇到了终止的元素,意味着表格已结束"""
                    table_containers.append(container)
                    container = None
                    break
            if container:
                table_containers.append(container)
        sorted_table_containers = sorted(table_containers, key=lambda x: x.get_sort_val())
        for table_container in sorted_table_containers:
            if table_container.indexs:
                table_item = table_container.table_item
                page_items[table_container.indexs[0]] = table_item
                for idx in table_container.indexs[1:]:
                    table_item.replace_items.append(page_items[idx])
                    page_items[idx] = None
                page_items[table_container.table_idx] = None

        return [item for item in page_items if item is not None]

    def run(self, items: List[AtomItem]) -> List[AtomItem]:
        rtn = []
        page_grouped_items = []
        for _, group in itertools.groupby(items, key=lambda x: x.start_page):
            page_grouped_items.append(list(group))
        for group in page_grouped_items:
            table_dealed_group = self.deal_table(group)
            rtn.extend(table_dealed_group)
        return rtn


class TableQualityRepair(BaseModel):
    """
        提高表格质量
        1) 去除空列数据
        2) 移除不符合要求的表格
    """
    COL_MIN_NUM: int = 2
    """表格最小列数量"""
    MAX_HEADER_CELL_LEN: int = 30
    UNNAME_HEADER_PREXI: str = "unname_"

    def _empty_header_deal(self, df: DataFrame) -> DataFrame:
        cols = df.columns.tolist()
        new_columns = []
        for idx, col in enumerate(cols):
            if col:
                new_columns.append(col)
            else:
                new_columns.append(self.UNNAME_HEADER_PREXI + str(idx))
        df.columns = new_columns
        return df

    def remove_empty_col(self, table: TextPDFTableAtomItem):
        """移除数据都为空的列"""
        df = self._empty_header_deal(table.df)

        def check_empty(data):
            counter = Counter([x for x in data if not x])
            empty_num = counter[None] + counter['']
            return empty_num == len(data)

        droped_cols = df.columns[df.apply(check_empty)]
        table.df = df.drop(columns=droped_cols)

    def is_validated_table(self, table: TextPDFTableAtomItem) -> bool:
        headers = table.df.columns.tolist()
        flag = all(len(header) < self.MAX_HEADER_CELL_LEN for header in headers)
        flag2 = len(headers) >= self.COL_MIN_NUM
        return flag and flag2

    def run(self, items: List[AtomItem]) -> List[AtomItem]:
        rtn = []
        for item in items:
            if item.item_type == TAtomItem.TABLE:
                table: TextPDFTableAtomItem = item
                self.remove_empty_col(table)
                if self.is_validated_table(table):
                    rtn.append(item)
                else:
                    rtn.extend(table.replace_items)
            else:
                rtn.append(item)
        not_empty_rtn =  [item for item in rtn if item]
        return not_empty_rtn


class TextPdfRepair(BaseModel):
    cross_page_table_repair: CrossPageTableRepair = CrossPageTableRepair()
    table_desc_repair: TableDescRepair = TableDescRepair()
    image_desc_repair: ImageDescRepair = ImageDescRepair()
    table_pos_repair: TablePosRepair = TablePosRepair()
    image_pos_repair: ImagePosRepair = ImagePosRepair()
    table_quality_repair: TableQualityRepair = TableQualityRepair()

    @staticmethod
    def adjust_table(table_item: TableAtomItem):
        # 删除数据为空字符串|None的列
        df = table_item.df

        def check_empty(data):
            counter = Counter([x for x in data if not x])
            empty_num = counter[None] + counter['']
            return empty_num == len(data)

        table_item.df = df.drop(columns=df.columns[df.apply(check_empty)])

    def run(self, items: List[AtomItem]) -> List[AtomItem]:
        items = self.image_pos_repair.run(items)
        items = self.table_pos_repair.run(items)
        items = self.cross_page_table_repair.run(items)
        items = self.table_quality_repair.run(items)
        items = self.table_desc_repair.run(items)
        items = self.image_desc_repair.run(items)
        return items


class TextPdfTitleRepair(BaseModel):
    tconn: TitleConnector

    def run(self, titles: List[TitleNode], items: List[AtomItem]) -> List[AtomItem]:
        """
        标题链接到item上
        """
        has_index_items: List[tuple[AtomItem, int]] = []
        for index, item in enumerate(items):
            has_index_items.append((item, index))
        title_conn_pos_dict: Dict[int, TitleNode] = {}
        cur_find_pos = 0
        for title in titles:
            candcates = has_index_items[cur_find_pos:]
            new_pos = self.tconn.find_similar_title(title, candcates)
            if new_pos < 0:
                continue
            title_conn_pos_dict[new_pos] = title
            cur_find_pos = new_pos
        # 替换处理
        final_items = []
        for index, item in enumerate(items):
            if index in title_conn_pos_dict:
                title = title_conn_pos_dict[index]
                title_item = TitleAtomItem.instance(title.title, title.title_level, item.start_page)
                final_items.append(title_item)
            else:
                final_items.append(item)
        return final_items
