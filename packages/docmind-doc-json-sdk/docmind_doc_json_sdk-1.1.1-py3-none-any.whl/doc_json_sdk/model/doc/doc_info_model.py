from dataclasses import dataclass

from doc_json_sdk.model.doc.page_model import PageModel
from doc_json_sdk.model.enums.document_type_enum import DocumentTypeEnum


@dataclass()
class DocInfoModel:
    # 文件类型
    __doc_type: str
    # 处理图片的dpi
    __dpi: int = 0
    # 文档每页图片的信息
    __pages: [] = None
    # 文件Url信息
    __doc_url: str = ''
    # 原始文件名称
    __original_doc_name: str = ''
    # 文件存储路由Key
    __file_storage_key: str = ''
    # request id
    __request_id: str = ''

    def __init__(self, doc_info_model: {}):
        self.__doc_type = doc_info_model['docType']
        self.__pages = []
        self.__request_id = doc_info_model["requestId"] if "requestId" in doc_info_model else None
        if "pages" in doc_info_model and doc_info_model['pages']:
            for i in doc_info_model['pages']:
                if isinstance(i,PageModel):
                    self.__pages.append(i)
                else:
                    self.__pages.append(PageModel(i))

    def get_request_id(self) -> str:
        return self.__request_id

    def get_doc_type(self) -> str:
        return self.__doc_type

    def get_dpi(self) -> int:
        return self.__dpi

    def get_pages(self) -> []:
        return self.__pages

    def get_page_count(self) -> int:
        if len(self.__pages) != 0:
            return len(self.__pages)
        else:
            return 0

    def get_document_type_enum(self) -> DocumentTypeEnum:
        return DocumentTypeEnum.get_document_type_by_suffix(self.__doc_type)
