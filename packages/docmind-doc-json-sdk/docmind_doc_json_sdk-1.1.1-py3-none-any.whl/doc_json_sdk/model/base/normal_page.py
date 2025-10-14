from dataclasses import dataclass

from doc_json_sdk.utils.hash import hash_code


@dataclass()
class NormalPage:
    # 通用页面名称
    __name: str
    # 通用页面默认高度
    __height: int
    # 通用页面默认宽度
    __width: int
    # 通用页面默认左边距
    __left: int
    # 通用页面默认右边距
    __right: int
    # 通用页面默认上边距
    __top: int
    # 通用页面默认下边距
    __bottom: int
    # 通用页面默认页眉距离
    __header: int
    # 通用页面默认页码距离
    __footer: int
    # 通用页面基准行高
    __line_height: int

    # 获取内容边界高度
    def get_margin_height(self) -> int:
        return self.__height - self.__top - self.__bottom

    # 获取内容边界宽度
    def get_margin_width(self) -> int:
        return self.__width - self.__right - self.__left

    def __eq__(self, normal_page: object) -> bool:
        if self is normal_page:
            return True
        if not isinstance(normal_page, NormalPage):
            return False
        that: NormalPage = NormalPage(normal_page)
        return (that.__name == self.__name and that.__height == self.__height and
                that.__width == self.__width and that.__left == self.__left and
                that.__right == self.__right and that.__top == self.__top and
                that.__bottom == self.__bottom and that.__header == self.__header and
                that.__footer == self.__footer)

    def clone(self) -> object:
        return self

    def __hash__(self) -> int:
        return hash_code([self.__name, self.__height, self.__width, self.__left, self.__right,
                          self.__top, self.__bottom, self.__header, self.__footer])
