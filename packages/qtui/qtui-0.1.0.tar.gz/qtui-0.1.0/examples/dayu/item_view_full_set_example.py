from qtpy import QtWidgets

import examples.dayu._mock_data as mock
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.item_view_full_set import MItemViewFullSet
from qtui.dayu.push_button import MPushButton


class ItemViewFullSetExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        item_view_set_table = MItemViewFullSet()
        item_view_set_table.set_header_list(mock.header_list)

        item_view_set_all = MItemViewFullSet(table_view=True, big_view=True)
        item_view_set_all.set_header_list(mock.header_list)

        refresh_button = MPushButton("Refresh Data")
        refresh_button.clicked.connect(self.slot_update_data)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Only Table View"))
        main_lay.addWidget(refresh_button)
        main_lay.addWidget(item_view_set_table)
        main_lay.addWidget(MDivider("Table View and Big View"))
        main_lay.addWidget(item_view_set_all)
        self.setLayout(main_lay)

        self.view_list = [
            item_view_set_table,
            item_view_set_all,
        ]
        self.slot_update_data()

    def slot_update_data(self):
        for view in self.view_list:
            view.setup_data(mock.data_list)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = ItemViewFullSetExample()
        MTheme().apply(test)
        test.show()
