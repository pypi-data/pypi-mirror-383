from dataclasses import dataclass
from enum import Enum


@dataclass()
class DataSourceEnum:
    class Elements(Enum):
        OCR = 'ocr'
        DIGITAL = 'digital'

    __source: str

    def __int__(self, source: str):
        self.__source = source

    @staticmethod
    def get_data_source_enum_by_code(code: str) -> Elements:
        res = []
        for i in DataSourceEnum.Elements:
            if i==code:
                res.append(i)
        if len(res) != 0:
            return res[0]
        else:
            raise EOFError
