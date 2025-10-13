from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QComboBox, QLineEdit
from PySide6.QtCore import Qt

from .table_widget import TableWidget


class PaginationWidget(QWidget):
    def __init__(self, parent=None, *args):
        # noinspection PyUnresolvedReferences
        super().__init__(parent.w if getattr(parent, 'w', None) is not None else parent, *args)
        # 先创建 table_widget，但不立即显示分页信息
        self.table_widget = TableWidget()
        self.table_widget.set_just_show_mode()

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 将表格控件添加到主布局中
        main_layout.addWidget(self.table_widget)

        # 创建分页控件的水平布局
        pagination_layout = QHBoxLayout()

        self.first_btn = QPushButton("首页")
        self.prev_btn = QPushButton("上一页")
        self.next_btn = QPushButton("下一页")
        self.last_btn = QPushButton("末页")
        self.info_label = QLabel()

        # 添加每页行数选择下拉框
        self.rows_per_page_combo = QComboBox()
        self.rows_per_page_combo.addItems(["10", "20", "50", "100"])
        self.rows_per_page_combo.setCurrentText(str(self.table_widget.rows_per_page))
        self.rows_per_page_label = QLabel("条/页")

        pagination_layout.addWidget(self.first_btn)
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.info_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addWidget(self.last_btn)
        pagination_layout.addStretch()  # 添加弹性空间
        pagination_layout.addWidget(self.rows_per_page_combo)
        pagination_layout.addWidget(self.rows_per_page_label)

        # 将分页控件添加到主布局中
        main_layout.addLayout(pagination_layout)

        # 连接按钮信号到包装函数，确保更新分页信息
        self.first_btn.clicked.connect(self._first_page)
        self.prev_btn.clicked.connect(self._previous_page)
        self.next_btn.clicked.connect(self._next_page)
        self.last_btn.clicked.connect(self._last_page)
        self.rows_per_page_combo.currentTextChanged.connect(self._change_rows_per_page)

        # 添加跳转到指定页的控件
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(50)
        self.page_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_input.setPlaceholderText("页码")
        self.go_page_btn = QPushButton("跳转")

        # 设置只能输入数字
        self.page_input.setValidator(QIntValidator(1, 999999))

        pagination_layout.addWidget(self.page_input)
        pagination_layout.addWidget(self.go_page_btn)

        # 连接跳转按钮信号
        self.go_page_btn.clicked.connect(self._go_to_page)

        # 初始化分页信息显示为默认值
        self._init_info_display()

    def _init_info_display(self):
        """初始化分页信息显示"""
        self.info_label.setText("第1/1页 (共0条记录)")

    def set_table_widget(self, table_widget):
        self.table_widget = table_widget
        self.update_info()

    def set_headers(self, headers: list):
        self.table_widget.set_headers(headers)

    def set_pagination(self, rows_per_page: int = 20):
        """
        设置分页参数
        :param rows_per_page: 每页显示行数
        """
        self.table_widget.set_pagination(rows_per_page)
        # 更新下拉框显示
        self.rows_per_page_combo.setCurrentText(str(rows_per_page))

    def set_data_source(self, data: list):
        self.table_widget.set_data_source(data)
        self.update_info()

    def _first_page(self):
        """首页按钮点击处理"""
        self.table_widget.first_page()
        self.update_info()

    def _previous_page(self):
        """上一页按钮点击处理"""
        self.table_widget.previous_page()
        self.update_info()

    def _next_page(self):
        """下一页按钮点击处理"""
        self.table_widget.next_page()
        self.update_info()

    def _last_page(self):
        """末页按钮点击处理"""
        self.table_widget.last_page()
        self.update_info()

    def _change_rows_per_page(self, text):
        """更改每页显示行数"""
        rows_per_page = int(text)
        # 保存当前页数据的起始位置
        current_start_index = (self.table_widget.current_page - 1) * self.table_widget.rows_per_page
        # 设置新的每页行数
        self.table_widget.set_pagination(rows_per_page)
        # 重新计算应该跳转到的页码
        new_page = current_start_index // rows_per_page + 1
        self.table_widget.go_to_page(new_page)
        self.update_info()

    def _go_to_page(self):
        """跳转到指定页"""
        page_text = self.page_input.text()
        if page_text:
            try:
                page = int(page_text)
                if 1 <= page <= self.table_widget.total_pages:
                    self.table_widget.go_to_page(page)
                    self.update_info()
                    self.page_input.clear()
            except ValueError:
                pass  # 无效输入，忽略

    def update_info(self):
        """更新分页信息显示"""
        info = self.table_widget.get_pagination_info()
        self.info_label.setText(f"第{info['current_page']}/{info['total_pages']}页")
        # 同步下拉框显示
        current_rows = str(info['rows_per_page'])
        if self.rows_per_page_combo.currentText() != current_rows:
            self.rows_per_page_combo.setCurrentText(current_rows)