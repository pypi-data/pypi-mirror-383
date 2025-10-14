from dataclasses import dataclass
from enum import Enum


from dataclasses import dataclass
from enum import Enum
from typing import List

@dataclass
class LayoutSubTypeEnum:
    class Elements(Enum):
        SINGLE_COLUMN = (['singleColumn', "forward", "middle", "backward"])
        MULTI_COLUMN = (['multiColumn', "multiField", "multiColumn"])
        TITLE = (['doc_name','doc_title','doc_subtitle','para_title'])
        TABLE_INFO = (['table_name','table_note'])
        FORMULA= (['formula'])
        CONTENT = (['cate_title','cate'])
        PARAGRAPH = (['para'])
        PICTURE = (['picture','logo'])
        PICTURE_INFO = (['pic_title','pic_caption'])
        NOTE = (['page_footer','page_header','page','footer_note','endnode','sidebar'])
        NONE = (['none'])

        def __init__(self, idp_layout_ex_types: List[str]):
            self.idpLayoutExTypes = idp_layout_ex_types

    idp_layout_ex_types: List[str]

    def __init__(self, idp_layout_ex_types: List[str]):
        self.idp_layout_ex_types = idp_layout_ex_types

    @staticmethod
    def get_layout_ex_type_enum_by_idp_ex_type(idp_layout_ex_type: str) -> Elements:
        tmp = idp_layout_ex_type.replace(' ', '')
        if not tmp:
            return LayoutSubTypeEnum.Elements.NONE

        for element in LayoutSubTypeEnum.Elements:
            if element.idpLayoutExTypes and idp_layout_ex_type in element.idpLayoutExTypes:
                return element

        return LayoutSubTypeEnum.Elements.NONE

