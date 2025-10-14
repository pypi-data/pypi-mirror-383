import math
from dataclasses import dataclass
from math import pow
from typing import List

from doc_json_sdk.model.base.pos_model import PosModel
from doc_json_sdk.model.enums.alignment_enum import AlignmentEnum
from doc_json_sdk.model.enums.data_source_enum import DataSourceEnum
from doc_json_sdk.model.enums.layout_sub_type_enum import LayoutSubTypeEnum
from doc_json_sdk.model.enums.layout_type_enum import LayoutTypeEnum


@dataclass
class LayoutModel(object):
    """

    版面基类

    """

    text: str
    """文本"""

    markdownContent: str
    """markdown information"""

    index: int
    """版面阅读顺序索引"""

    unique_id: str
    """版面信息唯一ID"""

    alignment: str
    """对齐方式"""

    page_num: []
    """版面所在页数"""

    pos: []
    """坐标"""

    type: str
    """视觉版面标签英文类型"""

    sub_type: str
    """语义版面标签"""

    child_layout: List
    """子版面: 该标题的子段落"""

    source: str = ''
    """数据来源"""

    spacing_before_layout: int = 0
    """距离前一个logout的水平间距"""

    spacing_after_layout: int = 0
    """距离后一个logout的水平间距"""

    vector_embeddings: List = None
    """文本向量 来源text生成"""

    layout_level: int = 0
    """版面级别：如一级版面、二级版面"""

    parent_layout = None
    """父版面：如标题为当前段落的父版面"""

    def __init__(self, layout_model: {}):
        self.text = layout_model['text']
        self.index = layout_model['index']
        self.unique_id = layout_model['uniqueId']
        self.alignment = layout_model['alignment'] if 'alignment' in layout_model else 'left'
        self.page_num = layout_model['pageNum']
        self.pos = [PosModel(i) for i in layout_model['pos']] if 'pos' in layout_model and layout_model['pos'] else []
        self.child_layout = []
        self.type = layout_model['type']
        self.sub_type = "" if 'subType' not in layout_model else layout_model['subType']
        self.markdownContent = layout_model['markdownContent'] if 'markdownContent' in layout_model and layout_model[
            'markdownContent'] is not None else None

    def set_child_layout(self, child_layout: []):
        self.child_layout = child_layout

    def set_parent_layout(self, parent_layout):
        self.parent_layout = parent_layout

    def set_layout_level(self, layout_level: int):
        self.layout_level = layout_level

    def get_layout_alignment_enum(self) -> AlignmentEnum:
        """

        获取 版面块 对齐类型枚举值

            :return: AlignmentEnum
        """
        return AlignmentEnum.get_alignment_enum_by_code(self.alignment)

    def get_layout_type_enum(self) -> LayoutTypeEnum:
        """

        获取版面块视觉版面

            :return: LayoutTypeEnum
        """
        return LayoutTypeEnum.get_layout_type_enum_by_idp_layout(self.type)

    def get_layout_sub_type_enum(self) -> LayoutSubTypeEnum:
        """

        获取版面块语义标签

            :return: LayoutSubTypeEnum
        """
        return LayoutSubTypeEnum.get_layout_ex_type_enum_by_idp_ex_type(self.sub_type)

    def get_data_source_enum(self) -> DataSourceEnum:
        """

        获取版面块信息来源

            :return: DataSourceEnum
        """
        return DataSourceEnum.get_data_source_enum_by_code(self.source)

    def get_html(self) -> str:
        return "<p>%s</p>" % self.text

    def get_text(self) -> str:
        head = ""
        if self.layout_level is not None and self.layout_level >= 0 and self.type.find("title") != -1:
            for i in range(self.layout_level + 1):
                head += "#"
            head += " "
            pass
        return head + self.text

    def get_sub_node_text(self) -> str:
        if self.child_layout is not None and len(self.child_layout) > 0:
            text = ""
            for child in self.child_layout:
                text += child.get_text() + " \n"
            return text
        else:
            return ""

    def get_page_num(self) -> []:
        return self.page_num

    def get_layout_level(self) -> int:
        return self.layout_level

    def get_pos_model_by_page_number(self, page_number: int) -> []:
        """

        跨页版面块

            :param page_number 页码
            :return: 坐标
        """
        index: int = self.page_num.index(page_number)
        if index != -1:
            return self.pos[index * 4: index * 4 + 4]
        else:
            raise OverflowError('pageNumber 超出layout页码范围值' + self.page_num)

    def get_min_x(self) -> int:
        """

        版面块  最左侧 X 位置

            :return: int
        """
        return min(min(self.pos[0].get_x(), self.pos[1].get_x()), min(self.pos[2].get_x(), self.pos[3].get_x()))

    def get_max_x(self) -> int:
        """

        版面块  最右侧 X 位置

            :return: int
        """
        return max(max(self.pos[0].get_x(), self.pos[1].get_x()), max(self.pos[2].get_x(), self.pos[3].get_x()))

    def get_min_y(self) -> int:
        """

        版面块  最上侧 Y 位置

            :return: int
        """
        return min(min(self.pos[0].get_y(), self.pos[1].get_y()), min(self.pos[2].get_y(), self.pos[3].get_y()))

    def get_max_y(self) -> int:
        """

        版面块  最下侧 Y 位置

            :return: int
        """
        return max(max(self.pos[0].get_y(), self.pos[1].get_y()), max(self.pos[2].get_y(), self.pos[3].get_y()))

    def get_x(self) -> int:
        """

        左上角 X 坐标

            :return: int
        """
        return self.pos[0].get_x()

    def get_x_by_page_number(self, pageNumber: int) -> int:
        """

        跨页面板块，左上角X坐标

            :param pageNumber 页码
            :return: 坐标
        """
        index: int = self.page_num.index(pageNumber)
        if index != -1:
            return self.pos[index * 4].get_x()
        else:
            raise OverflowError('pageNumber 超出layout页码范围值' + self.page_num)

    def get_y(self) -> int:
        """

        左上角 Y 坐标

            :return: int
        """
        return self.pos[0].get_y()

    def get_y_by_page_number(self, pageNumber: int) -> int:
        """

        跨页面板块，左上角Y坐标

            :param pageNumber: 页码
            :return: 坐标
        """
        index: int = self.page_num.index(pageNumber)
        if index != -1:
            return self.pos[index * 4].get_y()
        else:
            raise OverflowError('pageNumber 超出layout页码范围值' + self.page_num)

    def get_width(self) -> float:
        """

        版面块  宽度  计算两点间距离  d^2 = (x1-x2)^2 + (y1-y2)^2

        :return: float
        """
        return math.sqrt(
            pow(self.pos[0].get_x() - self.pos[1].get_x(), 2) + pow(self.pos[0].get_y() - self.pos[1].get_y(),
                                                                    2))

    def get_width_by_page_number(self, pageNumber: int) -> float:
        """

        跨页版面块  宽度  计算两点间距离  d^2 = (x1-x2)^2 + (y1-y2)^2

            :param pageNumber: 页码
            :return: float
        """
        index: int = self.page_num.index(pageNumber)
        if index != -1:
            return math.sqrt(pow(self.pos[index * 4].get_x() - self.pos[index * 4 + 1].get_x(), 2) +
                             pow(self.pos[index * 4].get_y() - self.pos[index * 4 + 1].get_y(), 2))
        else:
            raise OverflowError('pageNumber 超出layout页码范围值' + self.page_num)

    def get_height(self) -> float:
        """

        版面块  高度  计算两点间距离  d^2 = (x1-x2)^2 + (y1-y2)^2

            :return: float
        """
        return math.sqrt(
            pow(self.pos[0].get_x() - self.pos[3].get_x(), 2) + pow(self.pos[0].get_y() - self.pos[3].get_y(),
                                                                    2))

    def get_height_by_page_number(self, page_number: int) -> float:
        """

        跨页版面块  高度  计算两点间距离  d^2 = (x1-x2)^2 + (y1-y2)^2

            :param page_number: 页码
            :return: float
        """
        index: int = self.page_num.index(page_number)
        if index != -1:
            return math.sqrt(pow(self.pos[index * 4].get_x() - self.pos[index * 4 + 3].get_x(), 2) +
                             pow(self.pos[index * 4].get_y() - self.pos[index * 4 + 3].get_y(), 2))
        else:
            raise OverflowError('pageNumber 超出layout页码范围值' + self.page_num)

    def get_angle(self) -> float:
        """

        方框旋转坐标  0～360  从x正方向到y正方向

            :return: float
        """
        return math.atan(self.pos[1].get_x() - self.pos[0].get_x() + self.pos[1].get_y() - self.pos[0].get_y())

    def get_unique_id(self) -> str:
        """

        获取unique id

            :return: str
        """
        if self.unique_id is None or self.unique_id.strip() == '':
            if self.text is None:
                self.unique_id = str(self.page_num) + str(self.pos)
            else:
                self.unique_id = self.text + str(self.page_num) + str(self.pos)
        return self.unique_id

    def to_string(self) -> str:
        return '{text=' + self.text + '}'
