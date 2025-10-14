from dataclasses import dataclass
from enum import Enum



class DocumentTypeEnum(Enum):
    WORD = ['docx', 'doc']
    EXCEL = ['xlsx', 'xls']
    PPT = ['pptx', 'ppt']
    PDF = ['pdf', 'PDF']
    IMAGE = ['png', 'jpg', 'bmp', 'tiff', 'PNG', 'JPG']
    HTML = ['html']
    EPUB = ['epub']
    MOBI = ['mobi']
    TXT = ['txt']
    MARKDOWN = ['md','markdown']
    NONE = []

    @staticmethod
    def get_document_type_by_suffix(file_suffix: str):
        """
        根据文件后缀返回文档类型。

        :param file_suffix: 文件后缀
        :return: 对应的文档类型
        :raises ValueError: 如果未找到对应的文档类型
        """
        for document_type in DocumentTypeEnum:
            if file_suffix in document_type.value:
                return document_type
        return DocumentTypeEnum.NONE
