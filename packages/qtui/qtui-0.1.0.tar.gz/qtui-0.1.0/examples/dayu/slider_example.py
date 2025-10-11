import functools

from qtpy import QtCore, QtWidgets

from qtui.dayu.button_group import MPushButtonGroup
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.slider import MSlider
from qtui.dayu.spin_box import MSpinBox
from qtui.dayu.types import MButtonGroupData


class SliderExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MSlider")
        self._init_ui()

    def _init_ui(self):
        self.register_field("percent", 20)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("different orientation"))
        for orn in [QtCore.Qt.Orientation.Horizontal, QtCore.Qt.Orientation.Vertical]:
            line_edit_hor = MSlider(orn)
            line_edit_hor.setRange(1, 100)
            self.bind("percent", line_edit_hor, "value")
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(line_edit_hor)
            main_lay.addLayout(lay)
        spin_box = MSpinBox()
        spin_box.setRange(1, 100)
        self.bind("percent", spin_box, "value", signal="valueChanged")

        lay3 = QtWidgets.QHBoxLayout()
        button_grp = MPushButtonGroup()
        button_grp.set_button_list(
            [
                MButtonGroupData(
                    text="+", clicked=functools.partial(self.slot_change_value, 10)
                ),
                MButtonGroupData(
                    text="-", clicked=functools.partial(self.slot_change_value, -10)
                ),
            ]
        )
        lay3.addWidget(spin_box)
        lay3.addWidget(button_grp)
        lay3.addStretch()
        main_lay.addWidget(MDivider("data bind"))
        main_lay.addLayout(lay3)
        main_lay.addStretch()
        self.setLayout(main_lay)

    def slot_change_value(self, value: int):
        self.set_field("percent", max(0, min(self.field("percent") + value, 100)))


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = SliderExample()
        MTheme().apply(test)
        test.show()
