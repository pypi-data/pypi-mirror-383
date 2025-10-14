from dataclasses import dataclass
from typing import List

from doc_json_sdk.model.logic.kv_model import KvModel


@dataclass()
class TableKvModel:
    # 表格kv对信息
    __kvInfo: List[KvModel]
    # 表哥kv数组对
    __kvListIndo: List[List[KvModel]]
    # 单元格kv对关系
    __cellIdRelations: List[KvModel]

    def get_kv_info(self) -> List[KvModel]:
        return self.__kvInfo
