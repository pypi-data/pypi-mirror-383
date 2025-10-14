from typing import List

from doc_json_sdk.model.layout.layout_model import LayoutModel
from doc_json_sdk.model.layout.table.cell import Cell
from doc_json_sdk.model.logic.table_kv_model import TableKvModel


class TableLayoutModel(LayoutModel):
    """

    表格版面

    """
    num_col: int = 0
    """表格总列数"""

    num_row: int = 0
    """表格总行数"""

    cells = List[Cell]
    """单元格信息"""

    kv = List[TableKvModel]
    """表格Kv"""

    def __init__(self, table_layout_model: {}):
        super().__init__(table_layout_model)

        self.num_col = table_layout_model['numCol']
        self.num_row = table_layout_model['numRow']
        self.cells = []
        for i in table_layout_model['cells']:
            self.cells.append(Cell(i))

    def set_kv(self, kv: []):
        if kv is None:
            kv = []
        self.kv = kv

    def get_cell_by_col_row(self, startCol: int, startRow: int) -> Cell:
        """
        通过逻辑坐标获取单元格对象
            :param startCol: table logical index 起始单元格列 逻辑坐标
            :param startRow: table logical index 起始单元格行 逻辑坐标
            :return: cell
        """
        res = []
        for cell in self.cells:
            in_col: bool = False
            in_row: bool = False
            if cell.get_xsc()==cell.get_xec():
                in_col = (cell.get_xsc() == startCol)
            else:
                in_col = (cell.get_xsc() <= startCol & startCol <= cell.get_xec())

            if cell.get_ysc() == cell.get_yec():
                in_row = (cell.get_ysc() == startRow)
            else:
                in_row = (cell.get_ysc() <= startRow & startRow <= cell.get_yec())
            if in_col & in_row:
                res.append(cell)
        if len(res) != 0:
            return res[0]
        else:
            raise IndexError

    def get_num_col(self) -> int:
        """
        获取表格总列数
            :return:
        """
        if self.num_col is None:
            if self.cells is None:
                self.num_col = 0
            else:
                for cell in self.cells:
                    self.num_col = max(cell.get_xec(), self.num_col)
            self.num_col = self.num_col + 1
        return self.num_col

    def get_num_row(self) -> int:
        """
        获取表格总行数
            :return:
        """
        if self.num_row is None:
            if self.cells is None:
                self.num_row = 0
            else:
                for cell in self.cells:
                    self.num_row = max(cell.get_yec(), self.num_row)
            self.num_row = self.num_row + 1
        return self.num_row

    def get_html(self) -> str:
        """

        :return:
        """
        result = []
        if not self.cells:
            return ""
        result.append("<html>\n<meta http-equiv=\"Content-Type\" content=\"text/html;charset=UTF-8\">\n"
            + "<style type=text/css> " + " table tr td { border: 1px solid blue }\n"
            + "  table { border: 1px solid blue }\n" + "  span.note { font-size: 9px; color: red }\n"
            + "  div.margin_txt span { display:block;}\n</style>\n")
        result.append(f"<table id=\"table_{self.index}\">\n")
        XCellSize = self.num_col
        cell_is_null = [0] * (XCellSize + 1)
        result.append("<tr>")
        start = 0
        for cell in self.cells:
            if start >= XCellSize:
                result.append("</tr>\n")
                start = 0
                result.append("<tr>")
            Scell = '\n'.join([layout.text for layout in cell.get_layouts()])
            cell_is_null[cell.get_xsc()] += cell.get_yec() - cell.get_ysc()
            while start < cell.get_xsc():
                if cell_is_null[start] <= cell.get_ysc():
                    result.append(f"<td colspan=\"{1}\" rowspan=\"{1}\">{''}</td>")
                start += 1
            result.append(f"<td colspan=\"{cell.get_xec() - cell.get_xsc() + 1}\" rowspan=\"{cell.get_yec() - cell.get_ysc() + 1}\">{Scell}</td>")
            start += cell.get_xec() - cell.get_xsc() + 1
        result.append("</tr>\n")
        result.append("</table>\n")
        result.append("</html>\n")
        return ''.join(result)

    def get_text(self) -> str:
        mark_down: str = ''
        min_col = self.get_num_col()
        min_row = self.get_num_row()
        for cell in self.cells:
            min_col = min(min_col,cell.get_xsc())
            min_row = min(min_row,cell.get_ysc())

        for i in range(min_row,self.get_num_row()):
            mark_down += '| '
            for j in range(min_col,self.get_num_col()):
                try:
                    cell: Cell = self.get_cell_by_col_row(j, i)
                    for m in range(len(cell.get_layouts())):
                        layoutModel = cell.get_layouts()[m]
                        # table cell ignore paragraph level
                        mark_down += layoutModel.text
                        if m!=len(cell.get_layouts())-1:
                            mark_down += "<br>"
                except IndexError:
                    mark_down += ' '
                mark_down += '|'
            mark_down += '\n'
            if i == min_row:
                mark_down += '| '
                for j in range(self.get_num_col()):
                    mark_down += '---|'
                mark_down += '\n'
        return mark_down

    def get_cells(self) -> List[Cell]:
        return self.cells

    def get_kv(self):
        pass
