from enum import Enum


from enum import Enum
from typing import List, Optional

class LayoutTypeEnum:
    class Elements(Enum):
        # 从细粒度版面类型归一到粗粒度版面类型
        PARAGRAPH = ("text", [
            "title", "text", "docTitle", "docName",
            "subDocName", "docSubTitle", "subDocTitle", "subDocSubTitle",
            "contentTitle", "content", "firstLevelTitle", "secondLevelTitle",
            "title", "paragraph", "tablename", "tableNote", "imageTitle",
            "imageNote", "subNote", "multicolumn", "table_name",
            "table_note", "contents_title", "contents", "figure_name",
            "figure_note", "formula"
        ])

        TABLE = ("table", ["table"])

        IMAGE = ("image", [
            "figure", "image", "stamp", "qrcode", "note_line",
            "split_line", "header_line", "blank_line", "under_line",
            "footer_line", "column_line"
        ])

        FOOTER = ("footer", [
            "footer", "pageNumber", "foot", "foot_pagenum", "foot_image"
        ])

        HEADER = ("header", [
            "header", "head", "head_pagenum", "head_image"
        ])

        NOTE = ("note", [
            "footerNote", "other", "note", "corner_note", "end_note"
        ])

        TEXTBOX = ("textBox", ["writeBlock"])

        NONE = ("none", [""])

        def __init__(self, doc_layout_type: str, idp_layout_types: List[str]):
            self.docLayoutType = doc_layout_type
            self.idpLayoutTypes = idp_layout_types

    @staticmethod
    def get_layout_type_enum_by_idp_layout(idp_layout_type: str) -> Elements:
        tmp = idp_layout_type.replace(' ', '')
        if not tmp:
            return LayoutTypeEnum.Elements.NONE

        for elem in LayoutTypeEnum.Elements:
            if elem.value[0] == idp_layout_type or idp_layout_type in elem.value[1]:
                return elem

        return LayoutTypeEnum.Elements.NONE

