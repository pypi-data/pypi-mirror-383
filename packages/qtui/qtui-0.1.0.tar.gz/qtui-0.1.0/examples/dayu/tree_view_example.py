from qtpy import QtWidgets

import examples.dayu._mock_data as mock
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.item_model import MSortFilterModel, MTableModel
from qtui.dayu.item_view import MTreeView
from qtui.dayu.line_edit import MLineEdit
from qtui.dayu.push_button import MPushButton
from qtui.dayu.theme import MTheme


class TreeViewExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        model_1 = MTableModel()
        model_1.set_header_list(mock.header_list)
        model_sort = MSortFilterModel()
        model_sort.setSourceModel(model_1)

        tree_view = MTreeView()
        tree_view.setModel(model_sort)

        model_sort.set_header_list(mock.header_list)
        tree_view.set_header_list(mock.header_list)
        model_1.set_data_list(mock.tree_data_list)

        line_edit = MLineEdit().search_with_close().small()
        line_edit.textChanged.connect(model_sort.set_search_pattern)

        expand_all_button = MPushButton("Expand All").small()
        expand_all_button.clicked.connect(tree_view.expandAll)
        collapse_all_button = MPushButton("Collapse All").small()
        collapse_all_button.clicked.connect(tree_view.collapseAll)
        button_lay = QtWidgets.QHBoxLayout()
        button_lay.addWidget(expand_all_button)
        button_lay.addWidget(collapse_all_button)
        button_lay.addWidget(line_edit)
        button_lay.addStretch()

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addLayout(button_lay)
        main_lay.addWidget(tree_view)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = TreeViewExample()
        MTheme().apply(test)
        test.show()
