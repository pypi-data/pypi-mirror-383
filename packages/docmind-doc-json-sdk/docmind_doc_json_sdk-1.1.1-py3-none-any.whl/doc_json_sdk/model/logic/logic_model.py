from dataclasses import dataclass


@dataclass()
class LogicModel:
    # 逻辑信息列表
    doc_tree = []
    # 段落内容抽取结果
    paragraph_kv = []
    # 表哥抽取内容
    table_kv = []

    def __init__(self, logic_model: {}):
        if logic_model and 'docTree' in logic_model:
            self.doc_tree = logic_model['docTree']

    def get_doc_tree(self) -> []:
        return self.doc_tree

    def get_paragraph_kv(self) -> []:
        return self.paragraph_kv

    def get_table_kv(self) -> []:
        return self.table_kv
