from dataclasses import dataclass

from doc_json_sdk.utils.hash import hash_code


@dataclass()
class PosModel:
    # 横纵坐标，单位像素
    __x: int
    __y: int

    def __init__(self, pos_model: {}):
        self.__x = pos_model['x']
        self.__y = pos_model['y']

    def get_x(self) -> int:
        return self.__x

    def get_y(self) -> int:
        return self.__y

    def __eq__(self, o: object) -> bool:
        if self is o:
            return True
        if not isinstance(o, PosModel):
            return False
        pos: PosModel = PosModel(o)

        return self.__x.__eq__(pos.__x) and self.__y.__eq__(pos.__y)

    def __hash__(self) -> int:
        return hash_code([self.__x, self.__y])
