from dataclasses import dataclass


@dataclass()
class LogicInfo:
    # 索引id
    __uniqueId: str

    # 文档树层级
    __level: int

    # 子节点
    __link: {}

    # 父节点
    __backlink: {}

    def get_unique_id(self) -> str:
        return self.__uniqueId

    def get_level(self) -> int:
        return self.__level

    def get_backlink(self) -> {}:
        return self.__backlink

    def get_link(self) -> {}:
        return self.__link
