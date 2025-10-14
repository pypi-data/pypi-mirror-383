from dataclasses import dataclass
from enum import Enum


@dataclass()
class FontNameEnum:
    fontName: str

    class Elements(Enum):
        # 字体枚举
        SONG = '宋体'
        KAI_TI = '楷体'
        WEI_RUAN_YA_HEI = '微软雅黑'
        HEI_TI = '黑体'
        FANG_SONG = '仿宋'
        DENG_XIAN = '等线'
        TIMES_NEW_ROMAN = 'Times New Roman'
        ARIAL = 'Arial'

    @staticmethod
    def get_font_name_enum_by_font_str(self, font_str_name: str) -> Elements:
        res = []
        for i in self.Elements:
            if i==font_str_name:
                res.append(i)
        if len(res) == 0:
            return res[0]
        else:
            return FontNameEnum.Elements.WEI_RUAN_YA_HEI
