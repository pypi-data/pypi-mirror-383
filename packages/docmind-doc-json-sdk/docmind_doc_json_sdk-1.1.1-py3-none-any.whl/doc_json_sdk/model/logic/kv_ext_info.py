from dataclasses import dataclass


@dataclass()
class KvExtInfo:
    __tableId: str
    __valueLayoutId: str
    __keyLayoutId: str
    __valueConfidence: float
    __keyConfidence: float

    def get_table_id(self) -> str:
        return self.__tableId
