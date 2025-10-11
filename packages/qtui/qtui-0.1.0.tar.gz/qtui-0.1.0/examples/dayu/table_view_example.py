import functools
from typing import Any

from qtpy import QtCore, QtWidgets

import examples.dayu._mock_data as mock
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.item_model import MSortFilterModel, MTableModel
from qtui.dayu.item_view import MTableView
from qtui.dayu.line_edit import MLineEdit
from qtui.dayu.loading import MLoadingWrapper
from qtui.dayu.push_button import MPushButton
from qtui.dayu.theme import MTheme


class MFetchDataThread(QtCore.QThread):
    def __init__(self, parent: QtCore.QObject | None = None):
        super().__init__(parent)

    def run(self, *args: Any, **kwargs: Any):
        import time

        time.sleep(4)


class TableViewExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        model_1 = MTableModel()
        model_1.set_header_list(mock.header_list)
        model_sort = MSortFilterModel()
        model_sort.setSourceModel(model_1)

        table_small = MTableView(size=MTheme().small, show_row_count=True)
        table_grid = MTableView(size=MTheme().small, show_row_count=True)
        table_grid.setShowGrid(True)
        table_default = MTableView(size=MTheme().medium, show_row_count=True)
        thread = MFetchDataThread(self)

        self.loading_wrapper = MLoadingWrapper(widget=table_default, loading=False)
        thread.started.connect(
            functools.partial(self.loading_wrapper.set_dayu_loading, True)
        )
        thread.finished.connect(
            functools.partial(self.loading_wrapper.set_dayu_loading, False)
        )
        thread.finished.connect(functools.partial(table_default.setModel, model_sort))
        button = MPushButton(text="Get Data: 4s")
        button.clicked.connect(thread.start)
        switch_lay = QtWidgets.QHBoxLayout()
        switch_lay.addWidget(button)
        switch_lay.addStretch()
        table_large = MTableView(size=MTheme().large, show_row_count=False)

        table_small.setModel(model_sort)
        table_grid.setModel(model_sort)
        table_large.setModel(model_sort)
        model_sort.set_header_list(mock.header_list)
        table_small.set_header_list(mock.header_list)
        table_grid.set_header_list(mock.header_list)
        table_default.set_header_list(mock.header_list)
        table_large.set_header_list(mock.header_list)
        model_1.set_data_list(mock.data_list)

        line_edit = MLineEdit().search_with_close().small()
        line_edit.textChanged.connect(model_sort.set_search_pattern)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(line_edit)
        main_lay.addWidget(MDivider("Small Size"))
        main_lay.addWidget(table_small)
        main_lay.addWidget(MDivider("Default Size"))
        main_lay.addLayout(switch_lay)
        main_lay.addWidget(self.loading_wrapper)
        main_lay.addWidget(MDivider("Large Size (Hide Row Count)"))
        main_lay.addWidget(table_large)
        main_lay.addWidget(MDivider("With Grid"))
        main_lay.addWidget(table_grid)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application

    with application() as app:
        test = TableViewExample()
        MTheme().apply(test)
        test.show()
