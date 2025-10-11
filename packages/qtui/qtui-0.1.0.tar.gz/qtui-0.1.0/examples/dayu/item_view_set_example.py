from typing import cast

from qtpy import QtWidgets

import examples.dayu._mock_data as mock
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.item_view import MTreeView
from qtui.dayu.item_view_set import MItemViewSet
from qtui.dayu.push_button import MPushButton


class ItemViewSetExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        item_view_set_table = MItemViewSet(view_type=MItemViewSet.TableViewType)
        item_view_set_table.set_header_list(mock.header_list)
        item_view_set_list = MItemViewSet(view_type=MItemViewSet.ListViewType)
        item_view_set_list.set_header_list(mock.header_list)
        item_view_set_tree = MItemViewSet(view_type=MItemViewSet.TreeViewType)
        item_view_set_tree.set_header_list(mock.header_list)
        item_view_set_thumbnail = MItemViewSet(view_type=MItemViewSet.BigViewType)
        item_view_set_thumbnail.set_header_list(mock.header_list)

        item_view_set_search = MItemViewSet(view_type=MItemViewSet.TreeViewType)
        item_view_set_search.set_header_list(mock.header_list)
        item_view_set_search.searchable()
        expand_button = MPushButton("Expand All")
        expand_button.clicked.connect(
            cast(MTreeView, item_view_set_search.item_view).expandAll
        )
        coll_button = MPushButton("Collapse All")
        coll_button.clicked.connect(
            cast(MTreeView, item_view_set_search.item_view).collapseAll
        )
        item_view_set_search.insert_widget(coll_button)
        item_view_set_search.insert_widget(expand_button)

        refresh_button = MPushButton("Refresh Data")
        refresh_button.clicked.connect(self.slot_update_data)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Table View"))
        main_lay.addWidget(refresh_button)
        main_lay.addWidget(item_view_set_table)
        main_lay.addWidget(MDivider("List View"))
        main_lay.addWidget(item_view_set_list)
        main_lay.addWidget(MDivider("Tree View"))
        main_lay.addWidget(item_view_set_tree)
        main_lay.addWidget(MDivider("Big View"))
        main_lay.addWidget(item_view_set_thumbnail)
        main_lay.addWidget(MDivider("With Search line edit"))
        main_lay.addWidget(item_view_set_search)
        main_lay.addStretch()
        self.setLayout(main_lay)

        item_view_set_tree.setup_data(mock.tree_data_list)
        item_view_set_search.setup_data(mock.tree_data_list)
        self.view_list = [
            item_view_set_table,
            item_view_set_list,
            item_view_set_thumbnail,
        ]
        self.slot_update_data()

    def slot_update_data(self):
        for view in self.view_list:
            view.setup_data(mock.data_list)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = ItemViewSetExample()
        MTheme().apply(test)
        test.show()
