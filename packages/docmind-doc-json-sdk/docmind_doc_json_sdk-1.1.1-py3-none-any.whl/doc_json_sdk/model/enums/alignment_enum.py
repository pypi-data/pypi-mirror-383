from dataclasses import dataclass
from enum import Enum


@dataclass()
class AlignmentEnum:
    __code: str

    class Elements(Enum):
        LEFT = 'left'
        CENTER = 'center'
        RIGHT = 'right'

    def __int__(self, code: str):
        self.__code = code.lower()

    @staticmethod
    def get_alignment_enum_by_code(code: str) -> Elements:
        res = []
        for i in AlignmentEnum.Elements:
            if i==code:
                res.append(i)
        if len(res) == 0:
            return res[0]
        else:
            raise TypeError
