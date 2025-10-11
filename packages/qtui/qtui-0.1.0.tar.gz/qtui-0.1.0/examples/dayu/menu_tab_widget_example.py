import functools

from qtpy import QtCore, QtWidgets

from qtui.dayu.badge import MBadge
from qtui.dayu.label import MLabel
from qtui.dayu.menu_tab_widget import MMenuTabWidget
from qtui.dayu.message import MMessage
from qtui.dayu.theme import MTheme
from qtui.dayu.tool_button import MToolButton
from qtui.dayu.types import MButtonGroupData


class MenuTabWidgetExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MMenuTabWidget")
        self._init_ui()

    def _init_ui(self):
        item_list = [
            MButtonGroupData(
                text="Overview",
                svg="home_line.svg",
                clicked=lambda: MMessage.info("Home", parent=self),
            ),
            MButtonGroupData(
                text="My",
                svg="user_line.svg",
                clicked=functools.partial(MMessage.info, "Edit Account", parent=self),
            ),
            MButtonGroupData(
                text="Notice",
                svg="alert_line.svg",
                clicked=functools.partial(MMessage.info, "Notice", parent=self),
            ),
        ]
        tool_bar = MMenuTabWidget()
        tool_bar_huge = MMenuTabWidget()
        tool_bar_huge.set_dayu_size(MTheme().huge)
        tool_bar_huge_v = MMenuTabWidget(orientation=QtCore.Qt.Orientation.Vertical)
        tool_bar_huge_v.set_dayu_size(MTheme().huge)
        tool_bar.tool_bar_insert_widget(MLabel("DaYu").h4().secondary().strong())
        tool_bar_huge.tool_bar_insert_widget(MLabel("DaYu").h4().secondary().strong())
        dayu_icon = MLabel("DaYu").h4().secondary().strong()
        dayu_icon.setContentsMargins(10, 10, 10, 10)
        tool_bar_huge_v.tool_bar_insert_widget(dayu_icon)
        tool_bar.tool_bar_append_widget(
            MBadge.dot(
                show=True, widget=MToolButton().icon_only().svg("user_fill.svg").large()
            )
        )
        for index, data_dict in enumerate(item_list):
            tool_bar.add_menu(data_dict, index)
            tool_bar_huge.add_menu(data_dict, index)
            tool_bar_huge_v.add_menu(data_dict, index)

        tool_bar.tool_button_group.set_dayu_checked(0)
        tool_bar_huge.tool_button_group.set_dayu_checked(0)
        tool_bar_huge_v.tool_button_group.set_dayu_checked(0)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.setContentsMargins(0, 0, 0, 0)

        main_lay.addWidget(MLabel("Menu Tab Widget (Large)"))
        main_lay.addWidget(tool_bar)

        main_lay.addWidget(MLabel("Menu Tab Widget (Huge)"))
        main_lay.addWidget(tool_bar_huge)

        main_lay.addWidget(MLabel("Menu Vertical Tab Widget (Huge)"))
        main_lay.addWidget(tool_bar_huge_v)

        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = MenuTabWidgetExample()
        MTheme().apply(test)
        test.show()
