from qtpy import QtCore, QtWidgets

from qtui.dayu.check_box import MCheckBox
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.push_button import MPushButton
from qtui.dayu.qt import MIcon


class CheckBoxExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Example for MCheckBox")
        grid_lay = QtWidgets.QGridLayout()

        for index, (text, state) in enumerate(
            [
                ("Unchecked", QtCore.Qt.CheckState.Unchecked),
                ("Checked", QtCore.Qt.CheckState.Checked),
                ("Partially", QtCore.Qt.CheckState.PartiallyChecked),
            ]
        ):
            check_box_normal = MCheckBox(text)
            check_box_normal.setCheckState(state)

            check_box_disabled = MCheckBox(text)
            check_box_disabled.setCheckState(state)
            check_box_disabled.setEnabled(False)

            grid_lay.addWidget(check_box_normal, 0, index)
            grid_lay.addWidget(check_box_disabled, 1, index)

        icon_lay = QtWidgets.QHBoxLayout()
        for text, icon in [
            ("Maya", MIcon("app-maya.png")),
            ("Nuke", MIcon("app-nuke.png")),
            ("Houdini", MIcon("app-houdini.png")),
        ]:
            check_box_icon = MCheckBox(text)
            check_box_icon.setIcon(icon)
            icon_lay.addWidget(check_box_icon)

        check_box_bind = MCheckBox("Data Bind")
        label = MLabel()
        button = MPushButton(text="Change State")
        button.clicked.connect(
            lambda: self.set_field("checked", not self.field("checked"))
        )
        self.register_field("checked", True)
        self.register_field(
            "checked_text",
            lambda: "Yes!" if self.field("checked") else "No!!",
        )
        self.bind("checked", check_box_bind, "checked", signal="stateChanged")
        self.bind("checked_text", label, "text")

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Basic"))
        main_lay.addLayout(grid_lay)
        main_lay.addWidget(MDivider("Icon"))
        main_lay.addLayout(icon_lay)
        main_lay.addWidget(MDivider("Data Bind"))
        main_lay.addWidget(check_box_bind)
        main_lay.addWidget(label)
        main_lay.addWidget(button)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = CheckBoxExample()
        MTheme().apply(test)
        test.show()
