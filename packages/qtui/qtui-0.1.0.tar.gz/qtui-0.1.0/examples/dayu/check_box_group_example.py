from qtpy import QtCore, QtWidgets

from qtui.dayu.button_group import MCheckBoxGroup
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.push_button import MPushButton
from qtui.dayu.qt import MIcon
from qtui.dayu.types import MButtonGroupData


class CheckBoxGroupExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.app_data = [
            MButtonGroupData(text="Maya", icon=MIcon("app-maya.png")),
            MButtonGroupData(text="Nuke", icon=MIcon("app-nuke.png")),
            MButtonGroupData(text="Houdini", icon=MIcon("app-houdini.png")),
        ]
        radio_group_h = MCheckBoxGroup()
        radio_group_v = MCheckBoxGroup(orientation=QtCore.Qt.Orientation.Vertical)

        radio_group_h.set_button_list(self.app_data)
        radio_group_v.set_button_list(self.app_data)

        self.data_list = [
            "Beijing",
            "Shanghai",
            "Guangzhou",
            "Shenzhen",
            "Zhengzhou",
            "Shijiazhuang",
        ]
        radio_group_b = MCheckBoxGroup()
        radio_group_b.set_button_list(self.data_list)

        button = MPushButton(text="Change Value")
        button.clicked.connect(self.slot_button_clicked)

        label = MLabel()
        self.register_field("checked_app", ["Beijing", "Shanghai"])
        self.register_field(
            "checked_app_text", lambda: " & ".join(self.field("checked_app"))
        )
        self.bind(
            "checked_app", radio_group_b, "dayu_checked", signal="checked_changed"
        )
        self.bind("checked_app_text", label, "text")

        radio_group_tri = MCheckBoxGroup()
        radio_group_tri.set_context_menu_properties(
            show=True,
            select_all="select all",
            select_none="select none",
            select_invert="select invert",
        )
        radio_group_tri.set_button_list(self.app_data)
        self.register_field("check_grp", ["Maya"])
        self.bind(
            "check_grp", radio_group_tri, "dayu_checked", signal="checked_changed"
        )

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Orientation Qt.Horizontal"))
        main_lay.addWidget(radio_group_h)
        main_lay.addWidget(MDivider("Orientation Qt.Vertical"))
        main_lay.addWidget(radio_group_v)

        main_lay.addWidget(MDivider("Data Bind"))
        main_lay.addWidget(radio_group_b)
        main_lay.addWidget(label)
        main_lay.addWidget(button)

        main_lay.addWidget(MDivider("Try Context Menu"))
        main_lay.addWidget(radio_group_tri)
        main_lay.addStretch()
        self.setLayout(main_lay)

    @QtCore.Slot()
    def slot_button_clicked(self):
        import random

        start = random.randint(0, len(self.data_list))
        end = random.randint(start, len(self.data_list))
        self.set_field("checked_app", self.data_list[start:end])


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = CheckBoxGroupExample()
        MTheme().apply(test)
        test.show()
