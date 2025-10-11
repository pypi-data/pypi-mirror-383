from qtpy import QtWidgets

import examples.dayu._mock_data as mock
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.item_model import MSortFilterModel, MTableModel
from qtui.dayu.item_view import MListView
from qtui.dayu.line_edit import MLineEdit
from qtui.dayu.theme import MTheme


class ListViewExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        table_small = MListView(size=MTheme().small)
        table_default = MListView()
        table_large = MListView(size=MTheme().large)

        model_1 = MTableModel()
        model_1.set_header_list(mock.header_list)
        model_sort = MSortFilterModel()
        model_sort.setSourceModel(model_1)
        table_small.setModel(model_sort)
        table_default.setModel(model_sort)
        table_large.setModel(model_sort)
        model_sort.set_header_list(mock.header_list)
        table_small.set_header_list(mock.header_list)
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
        main_lay.addWidget(table_default)
        main_lay.addWidget(MDivider("Large Size"))
        main_lay.addWidget(table_large)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = ListViewExample()
        MTheme().apply(test)
        test.show()
