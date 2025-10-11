import functools

from qtpy import QtCore, QtWidgets

from qtui.dayu.button_group import MRadioButtonGroup
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.push_button import MPushButton
from qtui.dayu.qt import MIcon
from qtui.dayu.types import MButtonGroupData


class RadioButtonGroupExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        radio_group_h = MRadioButtonGroup()
        radio_group_h.set_button_list(["Apple", {"text": "Banana"}, {"text": "Pear"}])
        radio_grp_1_lay = QtWidgets.QHBoxLayout()
        radio_grp_1_lay.addWidget(radio_group_h)
        radio_grp_1_lay.addStretch()

        app_data = [
            MButtonGroupData(text="Maya", icon=MIcon("app-maya.png")),
            MButtonGroupData(text="Nuke", icon=MIcon("app-nuke.png")),
            MButtonGroupData(text="Houdini", icon=MIcon("app-houdini.png")),
        ]

        radio_group_v = MRadioButtonGroup(orientation=QtCore.Qt.Orientation.Vertical)
        radio_group_v.set_button_list(app_data)

        radio_group_button_h = MRadioButtonGroup()
        radio_group_button_h.set_button_list(app_data)
        radio_grp_h_lay = QtWidgets.QHBoxLayout()
        radio_grp_h_lay.addWidget(radio_group_button_h)
        radio_grp_h_lay.addStretch()

        radio_group_button_v = MRadioButtonGroup(
            orientation=QtCore.Qt.Orientation.Vertical
        )
        radio_group_button_v.set_button_list(app_data)

        self.register_field("value1", -1)
        self.register_field(
            "value1_text", functools.partial(self.value_to_text, "value1", app_data)
        )
        self.register_field("value2", 0)
        self.register_field(
            "value2_text", functools.partial(self.value_to_text, "value2", app_data)
        )
        self.register_field("value3", -1)
        self.register_field(
            "value3_text", functools.partial(self.value_to_text, "value3", app_data)
        )

        button1 = MPushButton(text="Group 1")
        button2 = MPushButton(text="Group 2")
        button3 = MPushButton(text="Group 3")
        button1.clicked.connect(functools.partial(self.slot_change_value, "value1"))
        button2.clicked.connect(functools.partial(self.slot_change_value, "value2"))
        button3.clicked.connect(functools.partial(self.slot_change_value, "value3"))

        self.bind("value1", radio_group_v, "dayu_checked", signal="checked_changed")
        self.bind(
            "value2", radio_group_button_h, "dayu_checked", signal="checked_changed"
        )
        self.bind(
            "value3", radio_group_button_v, "dayu_checked", signal="checked_changed"
        )
        self.bind("value1_text", button1, "text")
        self.bind("value2_text", button2, "text")
        self.bind("value3_text", button3, "text")

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("MRadioButtonGroup: orientation=Qt.Horizontal "))
        main_lay.addLayout(radio_grp_1_lay)
        main_lay.addWidget(MDivider("MRadioButtonGroup: orientation=Qt.Vertical"))
        main_lay.addWidget(radio_group_v)
        main_lay.addWidget(button1)
        main_lay.addWidget(
            MDivider("MRadioButtonGroup: orientation=Qt.Horizontal type=button")
        )
        main_lay.addLayout(radio_grp_h_lay)
        main_lay.addWidget(button2)
        main_lay.addWidget(
            MDivider("MRadioButtonGroup: orientation=Qt.Vertical, type=button")
        )
        main_lay.addWidget(radio_group_button_v)
        main_lay.addWidget(button3)
        main_lay.addStretch()
        self.setLayout(main_lay)

    def value_to_text(self, field: str, data_list: list[MButtonGroupData]) -> str:
        return (
            "Please Select One"
            if self.field(field) < 0
            else f"You Selected [{data_list[self.field(field)]['text']}]"
        )

    def slot_change_value(self, attr: str):
        import random

        self.set_field(attr, random.randrange(0, 3))


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = RadioButtonGroupExample()
        MTheme().apply(test)
        test.show()
