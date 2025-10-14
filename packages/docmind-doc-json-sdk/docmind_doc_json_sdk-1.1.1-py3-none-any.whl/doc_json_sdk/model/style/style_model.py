from dataclasses import dataclass
from typing import Optional

from doc_json_sdk.model.enums.font_name_enum import FontNameEnum


@dataclass()
class StyleModel:
    # 字体属性
    # 样式
    __style_id: Optional[int]
    # 字号大小
    __font_size: int
    # 下划线
    __underline: bool = False
    # 删除线
    __delete_line: bool = False
    # 加粗
    __bold: bool = False
    # 斜体
    __italic: bool = False
    # 字体名
    __font_name: str = '宋体'
    # 颜色
    __color: str = '000000'
    # 宽高比例 = 单字宽/单字高  charScale = charWith/charHeight
    __char_scale: float = 1.0

    def __init__(self, styleModel: dict):
        self.__style_id = styleModel['styleId']
        self.__underline = styleModel['underline']
        self.__delete_line = styleModel['deleteLine']
        self.__bold = styleModel['bold']
        self.__italic = styleModel['italic']
        self.__font_size =  styleModel['fontSize'] if "fontSize" in styleModel else 12
        self.__font_name = styleModel['fontName']
        self.__color = styleModel['color']
        self.__char_scale = styleModel['charScale']

    def get_style_id(self) -> int:
        return self.__style_id

    def get_underline(self):
        return self.__underline

    def get_delete_line(self):
        return self.__delete_line

    def get_bold(self):
        return self.__bold

    def get_italic(self):
        return self.__italic

    def get_font_size(self) -> int:
        return self.__font_size

    def get_color(self) -> str:
        return self.__color

    def get_font_name(self):
        return self.__font_name

    # 字体枚举值
    def get_font_name_enum(self):
        return FontNameEnum.get_font_name_enum_by_font_str(self.__font_name)

    def __eq__(self, obj: object) -> bool:
        if self is obj:
            return True

        other: StyleModel = StyleModel(obj)

        if obj is None or self.__font_size is None or other.__font_size is None:
            return False

        if not type(self) is type(obj):
            return False

        return (self.__underline == other.__underline and self.__delete_line == other.__delete_line
                and self.__bold == other.__bold and self.__italic == other.__italic and self.__font_size == other.__font_size
                and self.__font_name == other.__font_name and self.__color == other.__color
                and self.__char_scale == other.__char_scale)

    def to_string(self) -> str:
        return "StyleModel{" + "styleId=" + str(self.__style_id) + ", underline=" + str(self.__underline) + \
            ", deleteLine=" + str(self.__delete_line) + ", bold=" + str(self.__bold) + \
            ", italic=" + str(self.__italic) + ", fontSize=" + str(self.__font_size) + ", fontName=" + \
            self.__font_name + ", color=" + self.__color + '}'
