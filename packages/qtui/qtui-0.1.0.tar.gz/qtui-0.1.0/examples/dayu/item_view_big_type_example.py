import functools
from typing import cast

from qtpy import QtGui, QtWidgets

import examples.dayu._mock_data as mock
from qtui.dayu import utils as dayu_utils
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.item_view import MBigView
from qtui.dayu.item_view_set import MItemViewSet
from qtui.dayu.theme import MTheme
from qtui.dayu.tool_button import MToolButton


class ItemViewBigTypeExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        item_view_set_thumbnail = MItemViewSet(view_type=MItemViewSet.BigViewType)
        item_view_set_thumbnail.set_header_list(
            [
                {
                    "label": "Name",
                    "key": "name",
                    "searchable": True,
                    "font": lambda x, y: {"underline": True},
                    "icon": lambda x, y: y.get("icon"),
                }
            ]
        )
        add_button = MToolButton().svg("add_line.svg")
        add_button.clicked.connect(
            functools.partial(
                cast(MBigView, item_view_set_thumbnail.item_view).scale_size, 1.1
            )
        )
        minus_button = MToolButton().svg("minus_line.svg")
        minus_button.clicked.connect(
            functools.partial(
                cast(MBigView, item_view_set_thumbnail.item_view).scale_size, 0.8
            )
        )
        button_lay = QtWidgets.QHBoxLayout()
        button_lay.addWidget(minus_button)
        button_lay.addWidget(add_button)
        button_lay.addStretch()

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Big View"))
        main_lay.addLayout(button_lay)
        main_lay.addWidget(item_view_set_thumbnail)
        self.setLayout(main_lay)
        for data_dict in mock.data_list:
            icon = QtGui.QIcon(
                dayu_utils.generate_text_pixmap(
                    400,
                    400,
                    f"{data_dict.get('name', '')}_{data_dict.get('sex', '')}",
                    bg_color=MTheme().background_selected_color,
                )
            )
            data_dict.update({"icon": icon})
        item_view_set_thumbnail.setup_data(mock.data_list * 100)


if __name__ == "__main__":
    from qtui.dayu.qt import application

    with application() as app:
        test = ItemViewBigTypeExample()
        MTheme().apply(test)
        test.show()
