# coding=UTF-8
import os
from typing import List, Dict

from doc_json_sdk.model.enums.layout_type_enum import LayoutTypeEnum

from doc_json_sdk.model.document_model import DocumentModel
from doc_json_sdk.model.base.pos_model import PosModel
from doc_json_sdk.model.doc.page_model import PageModel
from doc_json_sdk.model.layout.image.image_layout_model import ImageLayoutModel
from doc_json_sdk.model.layout.layout_model import LayoutModel
from doc_json_sdk.model.layout.paragraph.block import Block
from doc_json_sdk.model.layout.paragraph.paragraph_layout_model import ParagraphLayoutModel
from doc_json_sdk.model.layout.table.cell import Cell
from doc_json_sdk.model.layout.table.table_layout_model import TableLayoutModel
from doc_json_sdk.model.style.style_model import StyleModel
from doc_json_sdk.utils.log_util import log
from deepdiff import DeepDiff

# 渲染绘制
def _build_tree(layous):
    tree = {}
    stack = [(tree, -1)]  # (当前节点, 当前层级)

    for item in layous:
        if item.type.find("title")==-1:
            continue
        name = item.get_text()
        level = item.get_layout_level()

        # 创建新节点
        new_node = {}

        # 确保当前层级的正确性
        while stack and stack[-1][1] >= level:
            stack.pop()

        # 将新节点添加到当前节点
        stack[-1][0][name] = new_node

        # 添加当前节点到栈中
        stack.append((new_node, level))

    return tree


class DocumentModelRender:
    enable_text_block: bool = False
    enable_chat_block: bool = False
    document_model: DocumentModel
    __style_map: {int, StyleModel}

    def __init__(self, document_model: DocumentModel):
        self.document_model = document_model

    def render_markdown_result(self):
        md_result = ""
        for layout in self.document_model.layouts:
            type_enum = layout.get_layout_type_enum()
            if (type_enum == LayoutTypeEnum.Elements.FOOTER or
                    type_enum == LayoutTypeEnum.Elements.HEADER or
                    type_enum == LayoutTypeEnum.Elements.NOTE):
                # ignore header and footer notes
                continue
            elif type_enum == LayoutTypeEnum.Elements.IMAGE:
                if layout.type.find("_line")!=-1:
                    continue
                md_result += layout.markdownContent if layout.markdownContent is not None else layout.text
            elif type_enum == LayoutTypeEnum.Elements.TABLE:
                md_result += layout.markdownContent if layout.markdownContent is not None else layout.text
            else:
                md_result += layout.markdownContent if layout.markdownContent is not None else layout.text
            if not md_result.endswith("\n"):
                md_result += "\n"
        return md_result

    def print_tree_title(self):
        tree = _build_tree(self.document_model.layouts)
        self._print_directory_structure(tree)
        pass

    def _print_directory_structure(self,directory, prefix=''):
        items = list(directory.items())
        total_items = len(items)

        for i, (name, content) in enumerate(items):
            connector = '└── ' if i == total_items - 1 else '├── '
            print(prefix + connector + name)
            if isinstance(content, dict):
                next_prefix = prefix + ('    ' if i == total_items - 1 else '│   ')
                self._print_directory_structure(content, next_prefix)

    def diff_other_document(self, compared_document: DocumentModel):
        def exclude_obj_callback(obj, path):
            if "pos" in path or "block" in path or "index" in path or "page_num" in path or "unique_id" in path:
                return True
            return False

        def include_obj_callback(obj, path):
            if issubclass(type(obj), LayoutModel) or "layout" in path:
                return True
            return False

        diff = DeepDiff(self.document_model, compared_document,include_obj_callback=include_obj_callback,exclude_obj_callback=exclude_obj_callback)
        log.info(diff.pretty())
        return diff
