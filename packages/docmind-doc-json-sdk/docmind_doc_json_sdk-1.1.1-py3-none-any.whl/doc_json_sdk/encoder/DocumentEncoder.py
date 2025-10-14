import json
from typing import Any

from doc_json_sdk.model.document_model import DocumentModel
from doc_json_sdk.model.base.pos_model import PosModel
from doc_json_sdk.model.doc.doc_info_model import DocInfoModel
from doc_json_sdk.model.doc.page_model import PageModel
from doc_json_sdk.model.layout.layout_model import LayoutModel
from doc_json_sdk.model.layout.image.image_layout_model import ImageLayoutModel
from doc_json_sdk.model.layout.paragraph.block import Block
from doc_json_sdk.model.layout.paragraph.paragraph_layout_model import \
    ParagraphLayoutModel
from doc_json_sdk.model.layout.paragraph.word_info import WordInfo
from doc_json_sdk.model.layout.table.cell import Cell
from doc_json_sdk.model.layout.table.table_layout_model import TableLayoutModel
from doc_json_sdk.model.logic.kv_model import KvModel
from doc_json_sdk.model.logic.logic_info import LogicInfo
from doc_json_sdk.model.logic.logic_model import LogicModel
from doc_json_sdk.model.logic.table_kv_model import TableKvModel
from doc_json_sdk.model.style.style_model import StyleModel


class DocumentEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, DocumentModel):
            return {
                "styles": [self.default(style) for style in obj.styles],
                "layouts": [self.default(layout) for layout in obj.layouts],
                "logics": self.default(obj.logics),
                # "docInfo": self.default(obj.get_doc_info()),
            }
        elif isinstance(obj, StyleModel):
            return {
                "styleId": obj.get_style_id(),
                "underline": obj.get_underline(),
                "deleteLine": obj.get_delete_line(),
                "bold": obj.get_bold(),
                "italic": obj.get_italic(),
                "fontSize": obj.get_font_size(),
                "fontName": obj.get_font_name(),
                "color": obj.get_color(),
            }
        elif isinstance(obj, LayoutModel):
            base_layout = {
                "text": obj.text,
                "index": obj.index,
                "uniqueId": obj.get_unique_id(),
                "alignment": obj.alignment,
                "pageNum": obj.page_num,
                "pos": obj.pos,
                "type": obj.type,
                "subType": obj.sub_type
            }
            if isinstance(obj, TableLayoutModel):
                base_layout["cells"] = [self.default(cell) for cell in obj.get_cells()]
                return base_layout
            elif isinstance(obj, ParagraphLayoutModel):
                base_layout["blocks"] = [self.default(block) for block in obj.get_blocks()]
                return base_layout
            elif isinstance(obj, ImageLayoutModel):
                return base_layout
        elif isinstance(obj, Block):
            return {
                "text": obj.get_text(),
                # "style": obj.get_style(),
                "styleId": obj.get_style_id(),
                "pos": obj.get_pos(),
                # "wordInfos": obj.get_word_info(),
            }
        elif isinstance(obj, WordInfo):
            return {

            }
        elif isinstance(obj, PosModel):
            return {"x": obj.get_x(), "y": obj.get_y()}
        elif isinstance(obj, Cell):
            return {
                "layouts": obj.get_layouts(),
                "xsc": obj.get_xsc(),
                "xec": obj.get_xec(),
                "ysc": obj.get_ysc(),
                "yec": obj.get_yec(),
                "type": obj.get_type(),
                "alignment": obj.get_alignment(),
                "cellId": obj.get_cell_id(),
                "pageNum": obj.get_page_num(),
                "pos": obj.get_pos(),
            }
        elif isinstance(obj, DocInfoModel):
            return {

            }
        elif isinstance(obj, PageModel):
            return {

            }
        elif isinstance(obj, LogicModel):
            return {
                "docTree": [self.default(logic_info) for logic_info in obj.get_doc_tree()],
                "paragraphKVs": [self.default(paragraph_info) for paragraph_info in obj.get_paragraph_kv()],
                "tableKVs": [self.default(table_info) for table_info in obj.get_table_kv()]
            }
        elif isinstance(obj, LogicInfo):
            return {
                "uniqueId": obj.get_unique_id(),
                "level": obj.get_level(),
                "link": obj.get_link(),
                "backlink": obj.get_backlink()
            }
        elif isinstance(obj, KvModel):
            return {
                "key": obj.get_key(),
                "value": obj.get_value,
                "extInfo": obj.get_ext_info()
            }
        elif isinstance(obj,TableKvModel):
            return {

            }
        elif isinstance(obj,dict):
            return obj
        else:
            print(type(obj))
            return super().default(obj)
