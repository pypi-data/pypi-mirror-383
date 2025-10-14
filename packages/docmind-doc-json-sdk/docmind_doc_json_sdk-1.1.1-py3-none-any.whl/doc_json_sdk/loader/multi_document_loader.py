import os

from doc_json_sdk.handler.document_handler_interface import DocumentHandler
from doc_json_sdk.loader.document_model_loader import DocumentModelLoader
from doc_json_sdk.utils.log_util import log
from multiprocessing import Pool, cpu_count


class MultiDocumentModelLoader(DocumentModelLoader):

    def __init__(self, handler: DocumentHandler = None, **kwargs):
        super().__init__(handler, **kwargs)
        self.__handler = handler

    def m_load(self, file_dir: str = None, file_url_list: list = None, request_list: list = None,
               save_json_dir: str = None, process_number=1, build_layout_image=False, build_doc_tree=False, **kwargs):
        """
        :param file_dir: 文件夹
        :param file_url_list: 文件url 列表
        :param request_list: request 列表
        :param save_json_dir: json保存文件夹
        :param process_number: 处理并发数
        :param build_layout_image:
        :param build_doc_tree:
        :param kwargs:
        :return:
        """
        param = {"save_json_dir": save_json_dir, "build_layout_image": build_layout_image,
                 "build_doc_tree": build_doc_tree}
        param.update(kwargs)
        task_queue = list()
        if file_dir is not None and os.path.exists(file_dir):
            for root, dirs, files in os.walk(file_dir):
                for file in files:
                    child_param = {"file_path": os.path.join(root, file)}
                    child_param.update(param)
                    task_queue.append(child_param)
            pass
        elif file_url_list is not None:
            for url in file_url_list:
                child_param = {"file_url": url}
                child_param.update(param)
                task_queue.append(child_param)
            pass
        elif request_list is not None:
            for request_id in request_list:
                child_param = {"request_id": request_id}
                child_param.update(param)
                task_queue.append(child_param)
            pass
        else:
            raise ValueError("file_dir,file_url_list,request_list")

        log.info("task %d with process %d"%(len(task_queue),process_number))
        documents = []
        with Pool(process_number) as thread_pool:
            results = []
            for param in task_queue:
                thread_return = thread_pool.apply_async(self.child_load,kwds=param)
                results.append(thread_return)
            for result in results:
                documents.append(result.get())
        return documents

    def child_load(self, **task_param):
        document = super().load(**task_param)
        return document
