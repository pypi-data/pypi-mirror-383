from qtpy import QtCore, QtWidgets

from qtui.dayu.button_group import MPushButtonGroup
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.push_button import MPushButton
from qtui.dayu.qt import MIcon
from qtui.dayu.theme import MTheme
from qtui.dayu.types import MButtonGroupData


class PushButtonGroupExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        button_config_list = [
            MButtonGroupData(
                text="Add",
                icon=MIcon("add_line.svg", "#fff"),
                dayu_type=MPushButton.ButtonType.Primary,
            ),
            MButtonGroupData(
                text="Edit",
                icon=MIcon("edit_fill.svg", "#fff"),
                dayu_type=MPushButton.ButtonType.Warning,
            ),
            MButtonGroupData(
                text="Delete",
                icon=MIcon("trash_line.svg", "#fff"),
                dayu_type=MPushButton.ButtonType.Danger,
            ),
        ]
        button_group_h = MPushButtonGroup()
        button_group_h.set_dayu_size(MTheme().large)
        button_group_h.set_button_list(button_config_list)
        h_lay = QtWidgets.QHBoxLayout()
        h_lay.addWidget(button_group_h)
        h_lay.addStretch()

        button_group_v = MPushButtonGroup(orientation=QtCore.Qt.Orientation.Vertical)
        button_group_v.set_button_list(button_config_list)
        h_lay_2 = QtWidgets.QHBoxLayout()
        h_lay_2.addWidget(button_group_v)
        h_lay_2.addStretch()

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(
            MLabel(
                "MPushButtonGroup is MPushButton collection. they are not exclusive."
            )
        )
        main_lay.addWidget(MDivider("MPushButton group: Horizontal & Small Size"))
        main_lay.addLayout(h_lay)
        main_lay.addWidget(MDivider("MPushButton group: Vertical & Default Size"))
        main_lay.addLayout(h_lay_2)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = PushButtonGroupExample()
        MTheme().apply(test)
        test.show()
