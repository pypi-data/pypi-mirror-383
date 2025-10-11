import functools
from collections.abc import Callable

from qtpy import QtWidgets

from qtui.dayu.breadcrumb import MBreadcrumb
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.message import MMessage
from qtui.dayu.types import MBreadcrumbData


class BreadcrumbExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MBreadcrumb")
        self._init_ui()

    def _init_ui(self):
        MMessage.config(duration=1)
        entity_list = [
            MBreadcrumbData(
                clicked=functools.partial(
                    self.slot_show_message, MMessage.info, 'Go to "Home Page"'
                ),
                svg="home_line.svg",
            ),
            MBreadcrumbData(
                text="pl",
                clicked=functools.partial(
                    self.slot_show_message, MMessage.info, 'Go to "pl"'
                ),
                svg="user_line.svg",
            ),
            MBreadcrumbData(
                text="pl_0010",
                clicked=functools.partial(
                    self.slot_show_message, MMessage.info, 'Go to "pl_0010"'
                ),
            ),
        ]
        no_icon_eg = MBreadcrumb()
        no_icon_eg.set_item_list(entity_list)

        separator_eg = MBreadcrumb(separator="=>")
        separator_eg.set_item_list(entity_list)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("normal"))
        main_lay.addWidget(no_icon_eg)
        main_lay.addWidget(MDivider("separator: =>"))
        main_lay.addWidget(separator_eg)

        main_lay.addStretch()
        self.setLayout(main_lay)

    def slot_show_message(
        self, func: Callable[[str, QtWidgets.QWidget], MMessage], config: str
    ):
        func(config, self)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = BreadcrumbExample()
        MTheme().apply(test)
        test.show()
