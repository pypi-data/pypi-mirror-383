from qtpy import QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.switch import MSwitch
from qtui.dayu.theme import MTheme


class SwitchExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MSwitch")
        self._init_ui()

    def _init_ui(self):
        check_box_1 = MSwitch()
        check_box_1.setChecked(True)
        check_box_2 = MSwitch()
        check_box_3 = MSwitch()
        check_box_3.setEnabled(False)
        lay = QtWidgets.QHBoxLayout()
        lay.addWidget(check_box_1)
        lay.addWidget(check_box_2)
        lay.addWidget(check_box_3)

        size_lay = QtWidgets.QFormLayout()
        size_lay.addRow("Huge", MSwitch().huge())
        size_lay.addRow("Large", MSwitch().large())
        size_lay.addRow("Medium", MSwitch().medium())
        size_lay.addRow("Small", MSwitch().small())
        size_lay.addRow("Tiny", MSwitch().tiny())

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Basic"))
        main_lay.addLayout(lay)
        main_lay.addWidget(MDivider("different size"))
        main_lay.addLayout(size_lay)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application

    with application() as app:
        test = SwitchExample()
        MTheme().apply(test)
        test.show()
