import numpy as np
import requests

from doc_json_sdk.model.base.normal_page import NormalPage


class PageModel:
    # 页面转换后的类型
    __image_type: str

    __source: str

    # 页面转图片后，图片的url
    image_url: str

    # 页面图宽
    __image_width: int

    # 页面图高
    __image_height: int

    # 当前页是所属文件的第几页
    __page_id_cur_doc: int

    # 单页id，是所有文档加起来的第几页
    __page_id_all_docs: int

    # 文件存储路由key
    __image_storage_key: str

    # 标准页面参数
    __normal_page: NormalPage

    # 页面内容起始X坐标
    __margin_x: int

    # 页面内容起始Y坐标
    __margin_y: int

    # 页面内容宽度
    __margin_width: int

    # 页面内容高度
    __margin_height: int

    # 宽度缩放因子
    __width_scale: float

    # 高度缩放因子
    __height_scale: float

    # 是否用了OCR
    __use_ocr: bool = False

    # 旋转角度
    __angle: float = 0.

    # pdf 每页整图信息(渲染图)  cv2的image对象
    __page_image: np.ndarray = None

    def __init__(self, page_model: dict):
        self.__image_type = page_model['imageType']
        self.image_url = page_model['imageUrl'] if 'imageStorageKey' in page_model else None
        self.__angle = page_model['angle']
        self.__source = "" if 'source' not in page_model else page_model['source']
        self.__image_width = page_model['imageWidth']
        self.__image_height = page_model['imageHeight']
        self.__page_id_cur_doc = page_model['pageIdCurDoc']
        self.__page_id_all_docs = page_model['pageIdAllDocs']
        self.__image_storage_key =page_model['imageStorageKey'] if 'imageStorageKey' in page_model else ""

    @property
    def image_type(self):
        return self.__image_type

    @property
    def height(self):
        return self.__image_height

    @property
    def width(self):
        return self.__image_width

    def get_page_id_cur_doc(self) -> int:
        return self.__page_id_cur_doc

    # def get_page_image(self) -> np.ndarray:
    #     if self.__page_image is None:
    #         self.__page_image = self.get_page_image_by_url()
    #     return self.__page_image
    #
    # # TODO 缺：先从本地找   再从URL替换 or 找
    # def get_page_image_by_url(self) -> np.ndarray:
    #     try:
    #         print(self.image_url)
    #         file = requests.get(self.image_url, stream=True)
    #         img = cv2.imdecode(np.fromstring(file.content, np.uint8), 1)
    #         return img
    #     except Exception as e:
    #         print(f'{self.image_url}无法访问或失效')


