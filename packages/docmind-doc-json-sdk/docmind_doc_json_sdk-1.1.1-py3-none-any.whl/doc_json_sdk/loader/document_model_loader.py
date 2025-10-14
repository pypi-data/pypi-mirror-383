# coding=UTF-8
import json
import requests
from doc_json_sdk.handler.document_handler_interface import DocumentHandler
from doc_json_sdk.model.doc.doc_info_model import DocInfoModel
from doc_json_sdk.model.doc.page_model import PageModel
from doc_json_sdk.model.document_model import DocumentModel
from doc_json_sdk.model.enums.layout_relation_enum import LayoutRelationEnum
from doc_json_sdk.model.layout.image.image_layout_model import ImageLayoutModel
from doc_json_sdk.model.layout.layout_model import LayoutModel
from doc_json_sdk.model.layout.paragraph.paragraph_layout_model import ParagraphLayoutModel
from doc_json_sdk.model.layout.table.table_layout_model import TableLayoutModel
from doc_json_sdk.model.logic.logic_model import LogicModel


class DocumentModelLoader:
    """

    直接装载documentModel对象 load document model from json, str or local file

    ----------------------

        :param doc_json_str: json string json字符串
        :param doc_json_dict: dict of doc json jsonDict对象
        :param document_path: file like pdf, image or office document 本地文件，文件类型参考IDP支持类型
    """
    __handler: DocumentHandler = None

    def load(self, file_path: str = None, file_url: str = None, request_id: str = None, doc_json_fp=None,
             save_json_path: str = None,
             build_layout_image=False, build_doc_tree=False, **kwargs):
        '''
        :param file_path:
        :param file_url:
        :param request_id:
        :param doc_json_fp:
        :param save_json_path:
        :param build_layout_image:
        :param build_doc_tree:
        :param kwargs:
            - formula_enhancement: 公式增强
            - structure_type: 配置参数，layout,doctree,default
            - reveal_markdown: 处理markdown
            - llm_enhancement: 大模型增加，只对DocumentParserWithCallbackHandler生效
            - enhancement_mode：VLM增强 str类型 ：VLM
        :return:
        '''
        if file_url is not None:
            doc_json_raw_info = self.__handler.get_document_json(file_url=file_url, **kwargs)
        elif file_path is not None:
            doc_json_raw_info = self.__handler.get_document_json(file_path=file_path, **kwargs)
        elif request_id is not None:
            doc_json_raw_info = self.__handler.get_document_json_by_request_id(request_id=request_id,**kwargs)
        elif doc_json_fp is not None:
            doc_json_raw_info = json.load(doc_json_fp)
            pass
        else:
            raise ValueError("file_path,file_url,request_id,doc_json_str is null")
        if doc_json_raw_info is None:
            return None
        doc_json_dict = doc_json_raw_info
        if "data" in doc_json_raw_info:
            doc_json_dict = doc_json_raw_info["data"]
        if "Data" in doc_json_raw_info:
            doc_json_dict = doc_json_raw_info["Data"]
        if "urlJson" in doc_json_dict:
            doc_json_dict = json.loads(requests.get(doc_json_dict['urlJson'],stream=True).content)
        if "documentModel" in doc_json_raw_info:
            doc_json_dict = doc_json_raw_info["documentModel"]
        if doc_json_dict is None or "layouts" not in doc_json_dict:
            raise RuntimeError(doc_json_raw_info)

        if save_json_path is not None:
            print("save result to %s" % save_json_path)
            with open(save_json_path, "w") as f:
                f.write(json.dumps(doc_json_dict, ensure_ascii=False, indent=4))

        document = DocumentModel(styles=[] if 'styles' not in doc_json_dict else doc_json_dict['styles'],
                                 layouts=doc_json_dict['layouts'],
                                 logics=LogicModel(
                                     None if 'logics' not in doc_json_dict else doc_json_dict['logics']),
                                 doc_info=None if 'docInfo' not in doc_json_dict else DocInfoModel(doc_json_dict['docInfo']),
                                 version=doc_json_dict['version'])
        if build_layout_image:
            self.__rebuild_layout_model(document)
        if build_doc_tree:
            self.__rebuild_doc_tree(document)

        return document

    def __init__(self, handler: DocumentHandler = None, **kwargs):
        self.__handler = handler

    def __rebuild_doc_tree(self, document: DocumentModel):
        """
        rebuild doc tree ,and set level info to layout
        :param doc_tree:
        :return:
        """
        if document.logics is None or document.logics.get_doc_tree() is None or len(document.logics.get_doc_tree()) == 0:
            print("doc tree is empty,ignoring")
            return
        doc_tree = document.logics.get_doc_tree()
        layout_cache: {} = {}

        for layout_model in document.layouts:
            layout_cache[layout_model.get_unique_id()] = layout_model

        max_depth = -1
        for logicInfo in doc_tree:
            layout_model: LayoutModel = layout_cache[logicInfo['uniqueId']]
            if layout_model.type.find("title") != -1:
                if logicInfo['level'] > max_depth:
                    max_depth = logicInfo['level']

        for logicInfo in doc_tree:
            layout_model: LayoutModel = layout_cache[logicInfo['uniqueId']]
            if max_depth != logicInfo['level']:
                layout_model.set_layout_level(logicInfo['level'])
            else:
                layout_model.set_layout_level(-1)
            parent_list: [] = logicInfo['backlink'][LayoutRelationEnum.Elements.PARENT.value] if len(
                logicInfo['backlink']) > 0 else []
            child_list: [] = logicInfo['link'][LayoutRelationEnum.Elements.CHILD.value] if len(
                logicInfo['link']) > 0 else []
            if len(parent_list) != 0:
                parent_id: str = parent_list[0]
                if LayoutRelationEnum.Elements.ROOT.value != parent_id:
                    layout_model.set_parent_layout(
                        layout_cache.get(parent_id) if layout_cache.get(parent_id) != None else "ROOT")
                if parent_id in layout_cache and layout_model not in layout_cache[parent_id].child_layout:
                    layout_cache[parent_id].child_layout.append(layout_model)

            if len(child_list) != 0:
                for childID in child_list:
                    if childID in layout_cache and layout_cache[childID] not in layout_model.child_layout:
                        layout_model.child_layout.append(layout_cache[childID])

    def __rebuild_layout_model(self, document: DocumentModel):
        """
        set kv info to layout
        :param layouts:
        :return:
        """
        layouts = document.layouts
        if len(layouts) == 0:
            return
        for layout in layouts:
            if isinstance(layout, ParagraphLayoutModel):
                self.__rebuild_paragraph_layout_model(document, layout)
            elif isinstance(layout, TableLayoutModel):
                self.__rebuild_table_layout_model(document, layout)
            elif isinstance(layout, ImageLayoutModel):
                # ignore
                # self.__rebuild_image_layout_model(layout)
                pass

    def __rebuild_paragraph_layout_model(self, document: DocumentModel, paragraph_layout_model: ParagraphLayoutModel):
        """
        set paragraph block, kv info to paragraph layout
        :param paragraph_layout_model:
        :return:
        """
        # paragraph  对象内部继续装载样式信息
        unique_id: str = paragraph_layout_model.get_unique_id()
        if len(paragraph_layout_model.get_blocks()) != 0 and len(document.styles) != 0:
            for block in paragraph_layout_model.get_blocks():
                block.set_style(document.styles[block.get_style_id()])

        # paragraph  对象内部装载kv信息
        if document.logics is not None and len(document.logics.get_paragraph_kv()) != 0:
            kv_list = []
            for i in document.logics.get_paragraph_kv():
                if i.get_ext_info().getKeyLayoutId() == unique_id or i.get_ext_info().getValueLayoutId() == unique_id:
                    kv_list.append(i)
            paragraph_layout_model.set_kv(kv_list)

    def __rebuild_table_layout_model(self, document: DocumentModel, table_layout_model: TableLayoutModel):
        """
        set table cell, kv info to table layout
        :param table_layout_model:
        :return:
        """
        # table 对象内容继续装载  样式信息
        unique_id: str = table_layout_model.get_unique_id()
        for cell in table_layout_model.get_cells():
            self.__rebuild_layout_model(cell.get_layouts())
        # table 内kv信息
        if document.logics is not None and len(
                document.logics.get_table_kv()) != 0:
            kv_list = []
            for tableKvModel in document.logics.get_table_kv():
                for kvModel in tableKvModel.get_kv_info():
                    if unique_id is kvModel.get_ext_info().get_table_id():
                        kv_list.append(kvModel)
            table_layout_model.set_kv(kv_list)

    # 将image中图片信息加载到对象中
    def __rebuild_image_layout_model(self, document: DocumentModel, image_layout_model: ImageLayoutModel):
        """
        set image (opencv image) to image layout
        :param image_layout_model:
        :return:
        """
        page_number: int = image_layout_model.get_page_num()[0]
        page_model: PageModel = document.get_page(page_number)
        x: int = max(image_layout_model.get_x(), 0)
        y: int = max(image_layout_model.get_y(), 0)
        if page_model is None:
            return
        width: float
        if image_layout_model.get_width() + x > page_model.width:
            width = page_model.width - x
        else:
            width = image_layout_model.get_width()
        height: float
        if image_layout_model.get_height() + y > page_model.height:
            height = page_model.height - y
        else:
            height = image_layout_model.get_height()
