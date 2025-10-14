from dataclasses import dataclass
from enum import Enum


@dataclass()
class LayoutRelationEnum:
    __code: str

    class Elements(Enum):
        PARENT = '上级'
        CHILD = '下级'
        CONTAIN = '包含'
        ROOT = 'ROOT'

    def __int__(self, code: str):
        self.__code = code

    def get_code(self):
        return self.__code

    @staticmethod
    def get_layout_relation_enum_by_code(code: str) -> Elements:
        res = []
        for i in LayoutRelationEnum.Elements:
            if i.value==code:
                res.append(i)
        if len(res) == 0:
            return LayoutRelationEnum.Elements.CONTAIN
        else:
            return res[0]
