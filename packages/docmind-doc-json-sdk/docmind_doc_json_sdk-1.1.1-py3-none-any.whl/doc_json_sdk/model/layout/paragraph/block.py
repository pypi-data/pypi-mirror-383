import math
from dataclasses import dataclass
from typing import List

from doc_json_sdk.model.base.pos_model import PosModel
from doc_json_sdk.model.layout.paragraph.word_info import WordInfo
from doc_json_sdk.model.style.style_model import StyleModel


@dataclass()
class Block:
    # 文本内容
    __text: str

    __style: StyleModel

    # 文本块坐标值
    __pos: List[PosModel]

    # 文本块样式id
    __style_id: int

    # 文本块 单字信息
    __word_info: List[WordInfo]

    def __init__(self, block: {}):
        self.__pos = []
        if 'pos' in block:
            for i in block['pos']:
                self.__pos.append(PosModel(i))
        self.__text = block['text']
        self.__style_id = block['styleId']
        self.__style = None
        self.__word_info = None

    def set_style(self, style: StyleModel):
        self.__style = style

    def get_text(self):
        return self.__text

    def get_style_id(self):
        return self.__style_id

    def get_pos(self) -> []:
        return self.__pos

    # 文本块最左侧X坐标
    def get_min_x(self) -> int:
        return min(min(self.__pos[0].get_x(), self.__pos[1].get_x()),
                   min(self.__pos[2].get_x(), self.__pos[3].get_x()))

    # 文本块最左侧X坐标
    def get_max_x(self) -> int:
        return max(max(self.__pos[0].get_x(), self.__pos[1].get_x()),
                   max(self.__pos[2].get_x(), self.__pos[3].get_x()))

    # 文本块最上侧Y坐标
    def get_min_y(self) -> int:
        return min(min(self.__pos[0].get_y(), self.__pos[1].get_y()),
                   min(self.__pos[2].get_y(), self.__pos[3].get_y()))

    # 文本块最下侧Y坐标
    def get_max_y(self) -> int:
        return max(max(self.__pos[0].get_y(), self.__pos[1].get_y()),
                   max(self.__pos[2].get_y(), self.__pos[3].get_y()))

    # 文本块  宽度
    def get_width(self) -> float:
        return float(math.sqrt(pow(self.__pos[0].get_x() - self.__pos[1].get_x(), 2) +
                               pow(self.__pos[0].get_y() - self.__pos[1].get_y(), 2)))

    # 文本块  高度
    def get_height(self) -> float:
        return float(math.sqrt(pow(self.__pos[0].get_x() - self.__pos[3].get_x(), 2) +
                               pow(self.__pos[0].get_y() - self.__pos[3].get_y(), 2)))

    def get_style(self):
        return self.__style

    def get_word_info(self):
        return self.__word_info
