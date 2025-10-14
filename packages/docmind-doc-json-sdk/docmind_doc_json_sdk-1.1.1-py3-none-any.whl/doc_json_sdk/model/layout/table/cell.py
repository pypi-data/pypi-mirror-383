import math
from dataclasses import dataclass
from typing import List
from doc_json_sdk.utils.log_util import log
from doc_json_sdk.model.base.pos_model import PosModel
from doc_json_sdk.model.layout.layout_model import LayoutModel


@dataclass()
class Cell:
    # 单元格板式信息
    __layouts: List[LayoutModel]
    # 起始单元格X横向逻辑坐标
    __xsc: int
    # 结束单元格X横向逻辑坐标
    __xec: int
    # 起始单元格Y纵向逻辑坐标
    __ysc: int
    # 结束单元格Y纵向逻辑坐标
    __yec: int
    # 单元格类型
    __type: str
    # 单元格对齐方式
    __alignment: str
    # 单元格Id（单格表格中唯一）
    __cell_id: int
    # 单元格所在页码
    __page_num: []
    # 单元格坐标
    __pos: [[]]

    def __init__(self, cell: {}):
        self.__layouts = []
        for i in cell['layouts']:
            self.__layouts.append(LayoutModel(i))
        self.__xsc = cell['xsc']
        self.__xec = cell['xec']
        self.__ysc = cell['ysc']
        self.__yec = cell['yec']
        self.__type = cell['type']
        self.__alignment = cell['alignment']
        self.__cell_id = cell['cellId']
        self.__page_num = cell['pageNum']
        self.__pos = cell['pos']

    def get_xsc(self) -> int:
        return self.__xsc

    def get_ysc(self) -> int:
        return self.__ysc

    def get_xec(self) -> int:
        return self.__xec

    def get_yec(self) -> int:
        return self.__yec

    def get_layouts(self) -> []:
        return self.__layouts

    # 跨页单元格 坐标信息
    # input: pageNumber
    # output: list(PosModel)
    def get_pos_model_by_page_number(self, page_number: int) -> []:
        if page_number in self.__page_num:
            index: int = self.__page_num.index(page_number)
            pos_models = []
            sub_pos = self.__pos[index]
            for i in range(4):
                pos_models.append(PosModel({'x': sub_pos[i * 2], 'y': sub_pos[i * 2 + 1]}))
            return pos_models
        else:
            log.warning('pageNumber 超出 Cell页码范围值' + str(self.__page_num))

    # 单元格左上角 X坐标
    def get_x(self) -> int:
        return min(self.__pos[0][0], self.__pos[0][2])

    # 跨页单元格左上角 X坐标
    def get_x_by_page_number(self, page_number: int) -> int:
        if page_number in self.__page_num:
            index: int = self.__page_num.index(page_number)
            return min(self.__pos[index][0], self.__pos[index][2])
        else:
            log.warning('pageNumber 超出 Cell页码范围值' + str(self.__page_num))

    # 单元格左上角 Y坐标
    def get_y(self) -> int:
        return min(self.__pos[0][1], self.__pos[0][7])

    # 跨页单元格左上角 Y坐标
    def get_y_by_page_number(self, page_number: int) -> int:
        if page_number in self.__page_num:
            index: int = self.__page_num.index(page_number)
            return min(self.__pos[index][1], self.__pos[index][7])
        else:
            log.warning('pageNumber 超出 Cell页码范围值' + str(self.__page_num))

    def get_width(self) -> float:
        return float(math.sqrt(pow(self.__pos[0][0] - self.__pos[0][2], 2) +
                               pow(self.__pos[0][1] - self.__pos[0][3], 2)))

    def get_width_by_page_number(self, page_number: int) -> float:
        if page_number in self.__page_num:
            index: int = self.__page_num.index(page_number)
            return float(math.sqrt(pow(self.__pos[index][0] - self.__pos[index][2], 2) +
                                   pow(self.__pos[index][1] - self.__pos[index][3], 2)))
        else:
            log.warning('pageNumber 超出 Cell页码范围值' + str(self.__page_num))

    def get_height(self) -> float:
        return float(math.sqrt(pow(self.__pos[0][0] - self.__pos[0][6], 2) +
                               pow(self.__pos[0][1] - self.__pos[0][7], 2)))

    def get_height_by_page_number(self, page_number: int) -> float:
        if page_number in self.__page_num:
            index: int = self.__page_num.index(page_number)
            return float(math.sqrt(pow(self.__pos[index][0] - self.__pos[index][6], 2) +
                                   pow(self.__pos[index][1] - self.__pos[index][7], 2)))
        else:
            log.warning('pageNumber 超出 Cell页码范围值' + str(self.__page_num))

    def get_type(self):
        return self.__type
        pass

    def get_alignment(self):
        return self.__alignment
        pass

    def get_cell_id(self):
        return self.__cell_id
        pass

    def get_page_num(self):
        return self.__page_num
        pass

    def get_pos(self):
        return self.__pos
        pass
