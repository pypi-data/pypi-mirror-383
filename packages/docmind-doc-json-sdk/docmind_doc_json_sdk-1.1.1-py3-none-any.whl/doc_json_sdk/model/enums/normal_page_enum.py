from dataclasses import dataclass
from enum import Enum

from doc_json_sdk.model.base.normal_page import NormalPage


@dataclass()
class NormalPageEnum:
    class Elements(Enum):
        A4PageSize = NormalPage(__name='A4PageSize', __height=20 * 842, __width=20 * 595,
                                __left=20 * 89, __right=20 * 89, __top=20 * 72, __bottom=20 * 72,
                                __header=20 * 36, __footer=20 * 36, __line_height=20 * 12)

        HorA4PageSize = NormalPage(__name='HorA4PageSize', __height=20 * 595, __width=20 * 842,
                                   __left=20 * 72, __right=20 * 72, __top=20 * 89, __bottom=20 * 89,
                                   __header=20 * 36, __footer=20 * 36, __line_height=20 * 12)

    normalPage: NormalPage

    def __int__(self, normal_page: NormalPage):
        self.normalPage = normal_page
