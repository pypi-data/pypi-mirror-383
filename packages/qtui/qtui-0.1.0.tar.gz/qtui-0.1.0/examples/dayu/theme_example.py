from qtpy import QtCore, QtWidgets

from qtui.dayu.button_group import MRadioButtonGroup
from qtui.dayu.check_box import MCheckBox
from qtui.dayu.combo_box import MComboBox
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.line_edit import MLineEdit
from qtui.dayu.push_button import MPushButton
from qtui.dayu.qt import MIcon
from qtui.dayu.slider import MSlider
from qtui.dayu.spin_box import MDateEdit, MSpinBox
from qtui.dayu.switch import MSwitch
from qtui.dayu.theme import MTheme
from qtui.dayu.types import MButtonGroupData


class ThemeExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        form_lay = QtWidgets.QFormLayout()
        form_lay.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        gender_grp = MRadioButtonGroup()
        gender_grp.set_button_list(
            [
                MButtonGroupData(text="Female", icon=MIcon("female.svg")),
                MButtonGroupData(text="Male", icon=MIcon("male.svg")),
            ]
        )

        country_combo_box = MComboBox().small()
        country_combo_box.addItems(["China", "France", "Japan", "US"])
        date_edit = MDateEdit().small()
        date_edit.setCalendarPopup(True)

        form_lay.addRow("Name:", MLineEdit().small())
        form_lay.addRow("Gender:", gender_grp)
        form_lay.addRow("Age:", MSpinBox().small())
        form_lay.addRow("Password:", MLineEdit().small().password())
        form_lay.addRow("Country:", country_combo_box)
        form_lay.addRow("Birthday:", date_edit)
        switch = MSwitch()
        switch.setChecked(True)
        form_lay.addRow("Switch:", switch)
        slider = MSlider()
        slider.setValue(30)
        form_lay.addRow("Slider:", slider)

        button_change = MPushButton(text="Change Theme")
        button_change.clicked.connect(self.slot_change_theme)

        button_lay = QtWidgets.QHBoxLayout()
        button_lay.addStretch()
        button_lay.addWidget(MPushButton(text="Submit").primary())
        button_lay.addWidget(MPushButton(text="Cancel"))

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addLayout(form_lay)
        main_lay.addWidget(MCheckBox("I accept the terms and conditions"))
        main_lay.addWidget(button_change)
        main_lay.addStretch()
        main_lay.addWidget(MDivider())
        main_lay.addLayout(button_lay)
        self.setLayout(main_lay)

    def slot_change_theme(self):
        import random

        color = random.choice(list(MTheme.GlobalColor))
        theme = random.choice(list(MTheme.ThemeType))
        MTheme().change_theme(self.window(), theme, color)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = ThemeExample()
        MTheme().apply(test)
        test.show()
