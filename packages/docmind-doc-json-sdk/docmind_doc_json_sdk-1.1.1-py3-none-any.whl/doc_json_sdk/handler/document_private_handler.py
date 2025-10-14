import json
import os
import requests

from typing import Dict, Callable
from doc_json_sdk.handler.document_handler_interface import DocumentHandler
from doc_json_sdk.utils.log_util import log


class PrivateDocumentExtractHandler(DocumentHandler):
    """
    私有化环境请求后端服务使用
    """
    __host: str = os.environ.get('PRIVATE_DOCMIND_HOST', f'127.0.0.1:7001')

    def __init__(self, host: str = None):
        if host is not None:
            self.__host = host
        log.info("ask host %s", self.__host)

    def get_document_json(self, file_path: str = None, file_url: str = None, **kwargs) -> Dict:
        reveal_markdown = True if "markdown_result" in kwargs and kwargs["markdown_result"] else False
        reveal_markdown = True if "reveal_markdown" in kwargs and kwargs["reveal_markdown"] else False
        kwargs["reveal_markdown"]=reveal_markdown
        if file_url is not None:
            response_id = self._submit_url(file_url, **kwargs)
        elif file_path is not None:
            raise ValueError("private_handler don't support file_path")
        else:
            raise ValueError("file_url is null")
        if response_id is None:
            raise ValueError("response_id is null")
        print(response_id)
        while 1:
            res = self._query(response_id, **kwargs)
            if res:
                if res["success"] == True and res["completed"] == True:
                    break
        return res

    def get_document_json_by_request_id(self, request_id: str, **kwargs):
        reveal_markdown = True if "markdown_result" in kwargs and kwargs["markdown_result"] else False
        use_url_response_body = True if "use_url_response_body" in kwargs and kwargs["use_url_response_body"] else False
        kwargs["reveal_markdown"]=reveal_markdown
        kwargs["use_url_response_body"]=use_url_response_body
        return self._query(request_id, **kwargs)

    def _submit_url(self, file_url: str, **kwargs):

        url = "http://{}/docMind/ayncDocStructure".format(self.__host)
        file_path = file_url[:file_url.rfind("?")] if (file_url.rfind("?") != -1) else file_url[file_url.rfind("/"):]
        formula_enhancement = True if "formula_enhancement" in kwargs and kwargs["formula_enhancement"] else False
        structure_type = kwargs["structure_type"] if "structure_type" in kwargs and kwargs[
            "structure_type"] else "doctree"

        param = {
            "option": structure_type,
            "bizIdentity": "publicDocStructure",
            "bizScene": "general",
            "fileName": file_path.rsplit("/", 1)[-1],
            "fileUrl": file_url,
            "formulaEnhancement": formula_enhancement,
        }
        param.update(kwargs)

        response = requests.request("POST", url, headers={
            'Content-Type': 'application/json'
        }, data=json.dumps(param),timeout=300)
        response = json.loads(response.text)
        return response["requestId"]

        pass

    def _query(self, response_id: str, reveal_markdown: bool = False,use_url_response_body:bool=False, **kwargs):
        url = "http://{}/docMind/queryDocStructureResult".format(self.__host)
        param = {
            "option": "doctree",
            "bizIdentity": "publicDocStructure",
            "bizScene": "general",
            "requestId": response_id,
            "revealMarkdown": reveal_markdown,
            "useUrlResponseBody":use_url_response_body
        }
        param.update(kwargs)

        response = requests.request("POST", url, headers={
            'Content-Type': 'application/json'
        }, data=json.dumps(param),timeout=300)
        response = json.loads(response.text)
        return response


class PrivateDigitalDocumentExtractHandler(DocumentHandler):
    '''
    私有化环境请求后端服务使用
    '''
    __host: str = os.environ.get('PRIVATE_DOCMIND_HOST', f'127.0.0.1:7001')

    def __init__(self, host: str = None):
        if host is not None:
            self.__host = host
        log.info("ask host %s", self.__host)

    def get_document_json(self, file_path: str = None, file_url: str = None, **kwargs) -> Dict:
        url = "http://{}/docMind/syncDocParser".format(self.__host)
        reveal_markdown = True if "markdown_result" in kwargs and kwargs["markdown_result"] else False
        param = dict()
        if file_url is not None:
            file_path = file_url[:file_url.rfind("?")] if (file_url.rfind("?") != -1) \
                else file_url[file_url.rfind("/"):]
            param = {
                "option": "digital",
                "bizIdentity": "publicDocParser",
                "bizScene": "general",
                "fileName": file_path.rsplit("/", 1)[-1],
                "fileUrl": file_url,
                "revealMarkdown": reveal_markdown
            }
        elif file_path is not None:
            raise ValueError("private_handler don't support file_path")
        else:
            raise ValueError("file_url is null")
        param.update(kwargs)
        response = requests.request("POST", url, headers={
            'Content-Type': 'application/json'
        }, data=json.dumps(param),timeout=300)
        response = json.loads(response.text)
        print(response["requestId"])
        return response

    def get_document_json_by_request_id(self, request_id: str, **kwargs):
        raise NameError("digital without method get_document_json_by_request_id")

class PrivateDocumentParserWithCallbackHandler(DocumentHandler):
    __callback: Callable[[Dict], None]
    __default_step: int

    def __init__(self, callback: Callable[[Dict], None],host: str = None,default_step: int = 20):
        if host is not None:
            self.__host = host
        log.info("ask host %s", self.__host)
        self.__callback = callback
        self.__default_step = default_step
        pass

    def get_document_json(self, file_path: str = None, file_url: str = None, **kwargs):
        if file_url is not None:
            response_id = self._submit_url(file_url, **kwargs)
        elif file_path is not None:
            raise ValueError("private_handler don't support file_path")
        else:
            raise ValueError("file_url is null")
        print(response_id)
        number_of_successful_parsing = 0
        number_of_processing = 0
        res = self._query_status(response_id)
        while 1:
            if number_of_processing < number_of_successful_parsing:
                result = self._query_group(response_id,number_of_processing,20)
                for layout in result["layouts"]:
                    self.__callback( layout)
                number_of_processing = number_of_processing + 20
            elif res and res['status'] == "success" and number_of_processing>=res['numberOfSuccessfulParsing']:
                break
            if res and res['status'] == "fail":
                break
            elif res and res['status'] == "success" and res['numberOfSuccessfulParsing'] > number_of_successful_parsing:
                number_of_successful_parsing = res['numberOfSuccessfulParsing']
            elif res and res['status'] == 'processing':
                res = self._query_status(response_id)
                number_of_successful_parsing = res['numberOfSuccessfulParsing']
            elif res and res['status'] == 'init':
                res = self._query_status(response_id)

    def _submit_url(self, file_url: str, **kwargs):
        url = "http://{}/docMind/model/chain/asyncDocParser".format(self.__host)
        file_path = file_url[:file_url.rfind("?")] if (file_url.rfind("?") != -1) else file_url[file_url.rfind("/"):]
        formula_enhancement = True if "formula_enhancement" in kwargs and kwargs["formula_enhancement"] else False
        structure_type = kwargs["structure_type"] if "structure_type" in kwargs and kwargs[
            "structure_type"] else "doctree"
        param = {
            "option": structure_type,
            "bizIdentity": "publicDocStreamStructure",
            "bizScene": "general",
            "fileName": file_path.rsplit("/", 1)[-1],
            "fileUrl": file_url,
            "formulaEnhancement": formula_enhancement,
        }
        param.update(kwargs)

        response = requests.request("POST", url, headers={
            'Content-Type': 'application/json'
        }, data=json.dumps(param),timeout=300)
        if response.status_code!=200:
            raise RuntimeError(response.text)
        response = json.loads(response.text)
        if response["code"]!=200:
            raise RuntimeError(response["msg"])
        return response["requestId"]

    def _query_status(self, request_id):
        url = "http://{}/docMind/model/chain/queryStatus".format(self.__host)
        param = {
            "requestId": request_id
        }
        response = requests.request("POST", url, headers={
            'Content-Type': 'application/json'
        }, data=json.dumps(param),timeout=300)
        response = json.loads(response.text)
        return response["data"]

    def _query_group(self, request_id, layout_num, layout_step_size):
        url = "http://{}/docMind/model/chain/queryResult".format(self.__host)
        param = {
            "requestId": request_id,
            "layoutNum":layout_num,
            "layoutStepSize":layout_step_size,
        }
        response = requests.request("POST", url, headers={
            'Content-Type': 'application/json'
        }, data=json.dumps(param),timeout=300)
        response = json.loads(response.text)
        return response["data"]

    def get_document_json_by_request_id(self, request_id: str):
        raise NameError("digital without method get_document_json_by_request_id")

