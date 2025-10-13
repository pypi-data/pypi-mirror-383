import typing

import prett6
import st
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem

from .. import ExcitedSignalInterface, RowChangedSignalInterface
from .. import ui_extension


@ui_extension
class TableWidget(QTableWidget, ExcitedSignalInterface, prett6.WidgetDictInterface, prett6.WidgetIndexInterface,
                  prett6.WidgetDictListInterface, RowChangedSignalInterface):
    keyPressFunc = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_page = 1
        self._rows_per_page = 20
        self._total_rows = 0
        self._data_source = []  # 存储所有数据

    def set_pagination(self, rows_per_page: int = 20):
        """
        设置分页参数
        :param rows_per_page: 每页显示行数
        """
        self._rows_per_page = rows_per_page

    @property
    def current_page(self) -> int:
        """获取当前页码"""
        return self._current_page

    @property
    def total_pages(self) -> int:
        """获取总页数"""
        return (self._total_rows + self._rows_per_page - 1) // self._rows_per_page if self._total_rows > 0 else 1

    @property
    def rows_per_page(self) -> int:
        """获取每页行数"""
        return self._rows_per_page

    def set_data_source(self, data: list):
        """
        设置数据源并刷新第一页
        :param data: 完整数据列表
        """
        self._data_source = data
        self._total_rows = len(data)
        self._current_page = 1
        self.load_page_data()

    def load_page_data(self):
        """
        加载当前页数据
        """
        # 清空现有数据
        self.setRowCount(0)

        # 计算当前页数据范围
        start_index = (self._current_page - 1) * self._rows_per_page
        end_index = min(start_index + self._rows_per_page, self._total_rows)

        # 获取当前页数据
        page_data = self._data_source[start_index:end_index]

        # 填充数据
        for row_data in page_data:
            self.dict.value = row_data
        self.index.value = 0

        # 调整列宽
        self.auto_resize_column_width()

    def go_to_page(self, page: int):
        """
        跳转到指定页
        :param page: 目标页码
        """
        if 1 <= page <= self.total_pages:
            self._current_page = page
            self.load_page_data()

    def next_page(self):
        """下一页"""
        if self._current_page < self.total_pages:
            self.go_to_page(self._current_page + 1)

    def previous_page(self):
        """上一页"""
        if self._current_page > 1:
            self.go_to_page(self._current_page - 1)

    def first_page(self):
        """首页"""
        self.go_to_page(1)

    def last_page(self):
        """末页"""
        self.go_to_page(self.total_pages)

    def get_pagination_info(self) -> dict:
        """
        获取分页信息
        :return: 包含分页信息的字典
        """
        return {
            'current_page': self._current_page,
            'total_pages': self.total_pages,
            'rows_per_page': self._rows_per_page,
            'total_rows': self._total_rows
        }

    def keyPressEvent(self, event):
        if self.keyPressFunc is not None:
            self.keyPressFunc(event)
        event.ignore()

    def set_row_changed_signal_connection(self):
        # noinspection PyUnresolvedReferences
        self.itemClicked.connect(self.row_changed_signal)

    def row_changed_signal(self):
        # noinspection PyUnresolvedReferences
        self.row_changed.emit_if_changed(self.currentRow())

    def set_excited_signal_connection(self):
        # noinspection PyUnresolvedReferences
        self.doubleClicked.connect(st.zero_para(self.excited.emit))

    def set_just_show_mode(self):
        self.auto_resize = True
        self.verticalHeader().hide()
        self.resizeColumnsToContents()
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def set_select_rows_mode(self):
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setStyleSheet("selection-background-color: lightBlue;selection-color: black;")
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.selectAll()
        # noinspection PyUnresolvedReferences
        self.itemClicked.connect(self.cancel_current_select)

    def set_column_hidden(self, header_name):
        header_labels = list(self.horizontalHeaderItem(i).text() for i in range(self.columnCount()))
        if header_name not in header_labels:
            raise ValueError("header_name doesn't match headers label")
        self.hideColumn(header_labels.index(header_name))

    def set_column_show(self, header_name):
        header_labels = list(self.horizontalHeaderItem(i).text() for i in range(self.columnCount()))
        if header_name not in header_labels:
            raise ValueError("header_name doesn't match headers label")
        self.showColumn(header_labels.index(header_name))

    def cancel_current_select(self):
        self.select_row_index = getattr(self, "select_row_index", 0)
        self.select_rows_num = getattr(self, "select_rows_num", 1)
        if self.currentRow() == self.select_row_index and \
                len(self.selectedItems()) == self.select_rows_num * self.columnCount():
            self.clearSelection()
        self.select_rows_num = len(self.selectedIndexes()) / self.columnCount()
        self.select_row_index = self.currentRow()

    def get_selected_list(self) -> typing.List[dict]:
        selected_ids = list(map(lambda x: x.row(), self.selectedIndexes()))
        selected_ids = list(set(selected_ids))
        selected_list = list(filter(lambda x: self.dict_list.value.index(x) in selected_ids, self.dict_list.value))
        return selected_list

    def get_selected_list_without_hidden_col(self) -> typing.List[dict]:
        selected_list = self.get_selected_list()
        header_labels = list(self.horizontalHeaderItem(i).text() for i in range(self.columnCount()))
        # if header_name not in header_labels:
        #     raise ValueError("header_name doesn't match headers label")
        # self.hideColumn(header_labels.index(header_name))
        hidden_columns = []
        for column_name in header_labels:
            if self.isColumnHidden(header_labels.index(column_name)):
                hidden_columns.append(column_name)
        for row in selected_list:
            for hidden_col in hidden_columns:
                del row[hidden_col]
        return selected_list

    def set_headers(self, headers: list):
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    @property
    def auto_resize(self):
        return getattr(self, 'resize', False)

    @auto_resize.setter
    def auto_resize(self, value: bool):
        setattr(self, 'resize', value)

    def get_item_style(self, x, y):
        style_dict = getattr(self, 'item_style', {})
        for xy in [(x, y), (None, y), (x, None), (None, None)]:
            if xy in style_dict.keys():
                return style_dict[xy]
        return None

    # add item style handle func
    def set_item_style(self, x, y, item_func):
        """
        :param x: row num, if it's None, will match all row.
        :param y: col num, if it's None, will match all col.
        :param item_func: func(item: QTableWidgetItem)
        """
        style_dict = getattr(self, 'item_style', {})
        style_dict[(x, y)] = item_func
        setattr(self, 'item_style', style_dict)

    def auto_resize_column_width(self):
        if self.auto_resize:
            self.resizeColumnsToContents()
            col_count = self.columnCount()
            col_width = sum(list([self.columnWidth(i) for i in range(col_count)]))
            if col_width < self.width():
                for i in range(col_count):
                    self.setColumnWidth(i, int(self.columnWidth(i) / col_width * self.width()))

    def resizeEvent(self, event):
        super(TableWidget, self).resizeEvent(event)
        self.auto_resize_column_width()

    class TableWidgetItem:
        def __init__(self, parent: 'TableWidget'):
            self.parent = parent

        @property
        def row_count(self):
            return self.parent.rowCount()

        @property
        def col_count(self):
            return self.parent.columnCount()

        def item_text(self, row, col):
            return self.parent.item(row, col).text()

    class DictItem(TableWidgetItem, prett6.WidgetDictItem):
        """get/set current table row text"""

        def get_value(self):
            if self.parent.index.value >= 0:
                current_row = self.parent.currentRow()
                col_count = self.parent.columnCount()
                value = dict()
                for i in range(col_count):
                    value[self.parent.horizontalHeaderItem(i).text()] = self.item_text(current_row, i)
                return value
            return None

        def set_value(self, value):
            assert isinstance(value, dict)
            if len(value) is not self.col_count:
                raise ValueError('Value length must equal to column count')

            texts = self.parent.dict_list.value
            assert isinstance(texts, list)
            if value is None:
                self.parent.index.value = 0
            else:
                for key, v in value.items():
                    value[key] = str(v)
                if value in texts:
                    self.parent.index.value = texts.index(value)
                else:
                    header_labels = list(self.parent.horizontalHeaderItem(i).text() for i in range(self.col_count))
                    self.parent.setRowCount(self.row_count + 1)
                    for i in range(self.col_count):
                        item_text = value[header_labels[i]]
                        if item_text is None:
                            raise ValueError("key value doesn't match headers label")
                        table_item = QTableWidgetItem(item_text)
                        table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item_handle = self.parent.get_item_style(self.row_count - 1, i)
                        if item_handle is not None:
                            item_handle(table_item)
                        self.parent.setItem(self.row_count - 1, i, table_item)
                    self.parent.index.value = self.row_count - 1
                    self.parent.auto_resize_column_width()

        def set_changed_connection(self):
            # noinspection PyUnresolvedReferences
            self.parent.currentCellChanged.connect(self.check_change)

    class IndexItem(TableWidgetItem, prett6.IndexItem):
        """get/set current select row"""

        def get_value(self):
            return self.parent.currentRow()

        def set_value(self, value):
            value = value or 0
            self.parent.selectRow(value)

        def set_changed_connection(self):
            # noinspection PyUnresolvedReferences
            self.parent.currentCellChanged(self.check_change)

    class DictListItem(TableWidgetItem, prett6.DictListItem):
        """ get all table_widget item text"""

        def get_value(self):
            table_texts = []
            for row in range(self.row_count):
                row_dict = dict()
                for col in range(self.col_count):
                    row_dict[self.parent.horizontalHeaderItem(col).text()] = self.item_text(row, col)
                table_texts.append(row_dict)
            return table_texts

        def set_value(self, value: list):
            value = value or []
            assert isinstance(value, list)

            for i in range(self.row_count):
                self.parent.removeRow(0)
            for row_dict in value:
                self.parent.dict.value = row_dict
            self.check_change()
