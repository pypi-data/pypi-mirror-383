from dataclasses import dataclass

from doc_json_sdk.model.logic.kv_ext_info import KvExtInfo


@dataclass
class KvModel:
    # key可能有多个
    __key: []
    # value 可能有多个
    __value: []
    # key 坐标值
    __keyPos: []
    # value坐标值
    __valuePos: []
    # key对应layout uniqueId
    # value对应 layout uniqueId
    __extInfo: KvExtInfo

    def get_key(self) -> []:
        return self.__key

    def get_value(self) -> []:
        return self.__value

    def get_ext_info(self) -> KvExtInfo:
        return self.__extInfo
