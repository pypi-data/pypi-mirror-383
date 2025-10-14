from abc import ABC, abstractmethod

class DocumentHandler(ABC):

    @abstractmethod
    def get_document_json(self, file_path: str = None, file_url: str = None, **kwargs):
        """
        get json object
        :param file_path:
        :param file_url:
        :param kwargs:
            - formula_enhancement
            - structure_type
            - reveal_markdown
        :return:
        """
        pass

    @abstractmethod
    def get_document_json_by_request_id(self, request_id: str):
        pass
