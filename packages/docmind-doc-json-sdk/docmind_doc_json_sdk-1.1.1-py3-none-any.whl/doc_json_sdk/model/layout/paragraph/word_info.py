from dataclasses import dataclass
from typing import List

from doc_json_sdk.model.base.pos_model import PosModel


@dataclass()
class WordInfo:
    # 文本内容
    __text: str
    # 坐标信息
    __pos: List[PosModel]

    def to_string(self) -> str:
        return 'WordInfo{text=' + self.__text + ',pos=' + self.__pos + '}'
