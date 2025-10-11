from qtpy import QtWidgets

from qtui.dayu.button_group import MRadioButtonGroup
from qtui.dayu.divider import MDivider
from qtui.dayu.drawer import MDrawer
from qtui.dayu.label import MLabel
from qtui.dayu.line_edit import MLineEdit
from qtui.dayu.push_button import MPushButton
from qtui.dayu.qt import MIcon, get_scale_factor
from qtui.dayu.spin_box import MDateEdit, MSpinBox


class DrawerExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MDrawer")
        self._init_ui()

    def _init_ui(self):
        scale_x, _ = get_scale_factor()
        self.button_grp = MRadioButtonGroup()
        self.button_grp.set_button_list(
            ["top", {"text": "right", "checked": True}, "bottom", "left"]
        )

        open_button_2 = MPushButton("Open").primary()
        open_button_2.clicked.connect(self.slot_open_button_2)
        placement_lay = QtWidgets.QHBoxLayout()
        placement_lay.addWidget(self.button_grp)
        placement_lay.addSpacing(int(20 * scale_x))
        placement_lay.addWidget(open_button_2)
        placement_lay.addStretch()

        new_account_button = MPushButton(
            text="New account", icon=MIcon("add_line.svg", "#fff")
        ).primary()
        new_account_button.clicked.connect(self.slot_new_account)
        new_account_lay = QtWidgets.QHBoxLayout()
        new_account_lay.addWidget(MLabel("Submit form in drawer"))
        new_account_lay.addWidget(new_account_button)
        new_account_lay.addStretch()

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Custom Placement"))
        main_lay.addLayout(placement_lay)
        main_lay.addWidget(MDivider("Submit form in drawer"))
        main_lay.addLayout(new_account_lay)

        main_lay.addWidget(MDivider("Preview drawer"))
        self.setLayout(main_lay)

    def slot_open_button(self):
        custom_widget = QtWidgets.QWidget()
        custom_lay = QtWidgets.QVBoxLayout()
        custom_lay.addWidget(MLabel("Some contents..."))
        custom_lay.addWidget(MLabel("Some contents..."))
        custom_lay.addWidget(MLabel("Some contents..."))
        custom_widget.setLayout(custom_lay)

        drawer = MDrawer("Basic Drawer", parent=self).left()
        scale_x, _ = get_scale_factor()
        drawer.setFixedWidth(int(300 * scale_x))
        drawer.set_widget(custom_widget)
        drawer.show()

    def slot_open_button_2(self):
        custom_widget = QtWidgets.QWidget()
        custom_lay = QtWidgets.QVBoxLayout()
        custom_lay.addWidget(MLabel("Some contents..."))
        custom_lay.addWidget(MLabel("Some contents..."))
        custom_lay.addWidget(MLabel("Some contents..."))
        custom_widget.setLayout(custom_lay)

        drawer = MDrawer("Basic Drawer", parent=self)
        drawer.set_dayu_position(
            self.button_grp.get_button_group().checkedButton().text()
        )

        scale_x, _ = get_scale_factor()
        drawer.setFixedWidth(int(300 * scale_x))
        drawer.set_widget(custom_widget)
        drawer.show()

    def slot_new_account(self):
        custom_widget = QtWidgets.QWidget()
        custom_lay = QtWidgets.QFormLayout()
        custom_lay.addRow("Name", MLineEdit())
        custom_lay.addRow("Age", MSpinBox())
        custom_lay.addRow("Birth", MDateEdit())
        custom_widget.setLayout(custom_lay)

        drawer = MDrawer("New account", parent=self)
        submit_button = MPushButton("Submit").primary()
        submit_button.clicked.connect(drawer.close)
        drawer.add_widget_to_bottom(MPushButton("Cancel"))
        drawer.add_widget_to_bottom(submit_button)
        scale_x, _ = get_scale_factor()
        drawer.setFixedWidth(int(300 * scale_x))
        drawer.set_widget(custom_widget)
        drawer.show()


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = DrawerExample()
        MTheme().apply(test)
        test.show()
