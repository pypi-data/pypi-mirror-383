import json
from dataclasses import dataclass
from typing import List
import dacite
from doc_json_sdk.model.doc.doc_info_model import DocInfoModel
from doc_json_sdk.model.doc.page_model import PageModel
from doc_json_sdk.model.enums.document_type_enum import DocumentTypeEnum
from doc_json_sdk.model.enums.layout_sub_type_enum import LayoutSubTypeEnum
from doc_json_sdk.model.enums.layout_type_enum import LayoutTypeEnum
from doc_json_sdk.model.layout.image.image_layout_model import ImageLayoutModel
from doc_json_sdk.model.layout.layout_model import LayoutModel
from doc_json_sdk.model.layout.paragraph.paragraph_layout_model import \
    ParagraphLayoutModel
from doc_json_sdk.model.layout.table.table_layout_model import TableLayoutModel
from doc_json_sdk.model.logic.logic_model import LogicModel
from doc_json_sdk.model.style.style_model import StyleModel


@dataclass()
class DocumentModel:
    #     样式列表
    styles: List[StyleModel]
    #     版面信息列表
    layouts: List[LayoutModel]
    #     逻辑信息列表（段落层级树）
    logics: LogicModel
    #     文件信息
    doc_info: DocInfoModel
    #     doc-json 版本号
    version: str = "1.2.0"

    def __init__(self, styles: List, layouts: List, logics: LogicModel, doc_info: DocInfoModel, version: str):
        self.styles = [StyleModel(style) for style in styles]
        self.layouts = []
        for layout in layouts:
            type = LayoutTypeEnum.get_layout_type_enum_by_idp_layout(layout["type"])
            if type == LayoutTypeEnum.Elements.TABLE:
                # table layout model include cells
                self.layouts.append(TableLayoutModel(layout))
            elif type == LayoutTypeEnum.Elements.PARAGRAPH:
                # paragraph layout model include blocks
                self.layouts.append(ParagraphLayoutModel(layout))
            elif type == LayoutTypeEnum.Elements.IMAGE:
                self.layouts.append(ImageLayoutModel(layout))
            else:
                # Footer,Header,Note,TextBlock use default Layout
                self.layouts.append(LayoutModel(layout))
        self.logics = logics
        self.doc_info = doc_info
        self.version = version

    def get_text(self):
        text = ""
        for layout in self.layouts:
            type_enum = layout.get_layout_type_enum()
            if type_enum == LayoutTypeEnum.Elements.FOOTER or type_enum == LayoutTypeEnum.Elements.HEADER:
                # ignore header and footer
                continue
            if type_enum == LayoutTypeEnum.Elements.IMAGE:
                # ignore image todo: upload oss ,get snapUrl
                text += "![%s]()" % (layout.get_unique_id() + ".jpg") + "  \n"
                continue
            text += layout.get_text() + "  \n"
        return text

    def get_markdown(self):
        markdown = ""
        for layout in self.layouts:
            type_enum = layout.get_layout_type_enum()
            if type_enum == LayoutTypeEnum.Elements.FOOTER or type_enum == LayoutTypeEnum.Elements.HEADER:
                # ignore header and footer
                continue
            if type_enum == LayoutTypeEnum.Elements.IMAGE:
                if "_line" in layout.type:
                    continue
                # ignore image todo: upload oss ,get snapUrl
                markdown += "![%s]()" % (layout.get_unique_id() + ".jpg") + "  \n"
                continue
            if layout.markdownContent is not None:
                markdown += layout.markdownContent + "  \n"
            else:
                markdown += layout.get_text() + "  \n"
        return markdown

    def get_html(self):
        text = "<html><body>\n"
        for layout in self.layouts:
            text += layout.get_html() + "\n"
        return text + "</body></html>"

    def get_sub_document_model(self, start_page_number: int, end_page_number: int):
        """
        get sub document model in [startPageNumber，endPageNumber)
        :param start_page_number: start page number (include)
        :param end_page_number: end page number (exclude)
        :return: document model
        """
        sub_layout = []
        pages = []
        for i in range(start_page_number, end_page_number, 1):
            sub_layout.extend(self.filter_layouts_by_page_number(i))
            pages.append(self.get_page(i))

        sub_doc_info: DocInfoModel = DocInfoModel(
            {'docType': self.doc_info.get_doc_type(), 'dpi': self.doc_info.get_dpi(), 'pages': pages})

        sub_document_model: DocumentModel = DocumentModel([],[],None,None,self.version)
        sub_document_model.layouts = sub_layout
        sub_document_model.styles = self.styles
        sub_document_model.doc_info = sub_doc_info
        sub_document_model.logics = self.logics
        return sub_document_model

    @property
    def doc_type(self) -> DocumentTypeEnum:
        """
        return document type
        :return: str
        :exception unknown type
        """
        try:
            return self.doc_info.get_document_type_enum()
        except TypeError:
            raise TypeError("unknown file type")

    @property
    def page_size(self) -> int:
        """
        return page size
        :return: int
        """
        return len(self.doc_info.get_pages()) if self.doc_info is not None else 0

    @property
    def pages(self) -> List[PageModel]:
        """
        return list of document page info
        :return:
        """
        return self.doc_info.get_pages()

    def get_page(self, page_number: int) -> PageModel:
        """
        return specified page by given page number
        :param page_number:
        :return:
        """
        for i in self.doc_info.get_pages():
            if i.get_page_id_cur_doc() == page_number:
                return i

    # ################layout function################################
    def filter_layouts_by_type(self, layout_type: LayoutTypeEnum) -> List[LayoutModel]:
        """
        filter layouts by visual layout type
        :param layout_type:
        :return: list of layouts
        """
        res = []
        for i in self.layouts:
            if i.get_layout_type_enum() == layout_type:
                res.append(i)
        return res

    def filter_layouts_by_sub_type(self, layout_sub_type: LayoutSubTypeEnum) -> List[LayoutModel]:
        """
        filter layouts by semantic layout type
        :param layout_sub_type:
        :return: list of layouts
        """
        res = []
        for i in self.layouts:
            if i in layout_sub_type.Elements:
                res.append(i)
        return res

    def filter_layouts_by_page_number(self, page_number: int) -> list[LayoutModel]:
        """
        filter layouts by page number
        :param page_number:
        :return: list of layouts
        """
        res = []
        for i in self.layouts:
            if page_number in i.get_page_num():
                res.append(i)
        return res

    def filter_layouts_by_unique_id(self, unique_id: str) -> LayoutModel:
        """
        filter layouts by unique
        :param unique_id:
        :return: list of layouts
        """
        for i in self.layouts:
            if unique_id == i.get_unique_id:
                return i
        print('此uniqueId(独立索引)不存在')

    # ##################logic function####################################
    def filter_layout_by_level(self, level: int) -> List[LayoutModel]:
        """
        filter layouts by doc tree level
        :param level: int
        :return: list of layouts
        """
        res = []
        for i in self.layouts:
            if level == i.get_layout_level:
                res.append(i)
        return res

