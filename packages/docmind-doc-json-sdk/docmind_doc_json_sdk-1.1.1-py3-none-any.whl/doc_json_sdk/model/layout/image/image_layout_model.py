import numpy as np

from doc_json_sdk.model.layout.layout_model import LayoutModel


class ImageLayoutModel(LayoutModel):
    """

    图片版面块信息

    """
    image: np.ndarray
    """image cv2 np.ndarray类型 """

    def __init__(self, layout_model: {}):
        super().__init__(layout_model)
        # self.image = layout_model['']

    def set_image(self, image: np.ndarray):
        self.image = image
