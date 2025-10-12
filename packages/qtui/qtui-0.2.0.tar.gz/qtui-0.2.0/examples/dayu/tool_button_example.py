from PySide6 import QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.tool_button import MToolButton


class ToolButtonExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MToolButton")
        self._init_ui()

    def _init_ui(self):
        size_lay = QtWidgets.QVBoxLayout()
        sub_lay1 = QtWidgets.QHBoxLayout()
        sub_lay1.addWidget(MToolButton().svg("left_line.svg").icon_only().huge())
        sub_lay1.addWidget(MToolButton().svg("right_line.svg").icon_only().large())
        sub_lay1.addWidget(MToolButton().svg("up_line.svg").icon_only())
        sub_lay1.addWidget(MToolButton().svg("up_line.svg").icon_only().small())
        sub_lay1.addWidget(MToolButton().svg("down_line.svg").icon_only().tiny())
        sub_lay1.addStretch()
        size_lay.addLayout(sub_lay1)

        button2 = MToolButton().svg("detail_line.svg").icon_only()
        button2.setEnabled(False)
        button7 = MToolButton().svg("trash_line.svg").icon_only()
        button7.setCheckable(True)
        state_lay = QtWidgets.QHBoxLayout()
        state_lay.addWidget(button2)
        state_lay.addWidget(button7)
        state_lay.addStretch()

        button_trash = MToolButton().svg("trash_line.svg").text_beside_icon()
        button_trash.setText("Delete")
        button_login = MToolButton().svg("user_line.svg").text_beside_icon()
        button_login.setText("Login")

        button_lay = QtWidgets.QHBoxLayout()
        button_lay.addWidget(button_trash)
        button_lay.addWidget(button_login)

        sub_lay2 = QtWidgets.QHBoxLayout()
        sub_lay2.addWidget(button2)
        sub_lay2.addWidget(button7)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("different button_size"))
        main_lay.addLayout(size_lay)
        main_lay.addWidget(MDivider("disabled & checkable"))
        main_lay.addLayout(state_lay)
        main_lay.addWidget(MDivider("type=normal"))
        main_lay.addLayout(button_lay)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = ToolButtonExample()
        MTheme().apply(test)
        test.show()
