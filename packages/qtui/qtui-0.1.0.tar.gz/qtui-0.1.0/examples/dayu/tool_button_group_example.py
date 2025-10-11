from qtpy import QtCore, QtWidgets

from qtui.dayu.button_group import MToolButtonGroup
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.qt import MIcon
from qtui.dayu.theme import MTheme
from qtui.dayu.types import MButtonGroupData


class ToolButtonGroupExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        tool_group_h = MToolButtonGroup(size=MTheme().small)
        tool_group_h.set_button_list(["Apple", {"text": "Banana"}, {"text": "Pear"}])
        tool_1_lay = QtWidgets.QHBoxLayout()
        tool_1_lay.addWidget(tool_group_h)
        tool_1_lay.addStretch()

        app_data = [
            MButtonGroupData(text="Maya", icon=MIcon("app-maya.png"), checkable=True),
            MButtonGroupData(text="Nuke", icon=MIcon("app-nuke.png"), checkable=True),
            MButtonGroupData(
                text="Houdini", icon=MIcon("app-houdini.png"), checkable=True
            ),
        ]

        tool_group_v = MToolButtonGroup(
            exclusive=True,
            size=MTheme().small,
            orientation=QtCore.Qt.Orientation.Vertical,
        )
        tool_group_v.set_button_list(app_data)

        tool_group_button_h = MToolButtonGroup()
        tool_group_button_h.set_button_list(app_data)
        tool_2_lay = QtWidgets.QHBoxLayout()
        tool_2_lay.addWidget(tool_group_button_h)
        tool_2_lay.addStretch()

        tool_grp_excl_true = MToolButtonGroup(
            orientation=QtCore.Qt.Orientation.Horizontal, exclusive=True
        )
        tool_grp_excl_true.set_button_list(
            [
                MButtonGroupData(
                    svg="table_view.svg", checkable=True, tooltip="Table View"
                ),
                MButtonGroupData(
                    svg="list_view.svg", checkable=True, tooltip="List View"
                ),
                MButtonGroupData(
                    svg="tree_view.svg", checkable=True, tooltip="Tree View"
                ),
                MButtonGroupData(
                    svg="big_view.svg", checkable=True, tooltip="Big View"
                ),
            ]
        )
        tool_grp_excl_true.set_dayu_checked(0)
        tool_excl_lay = QtWidgets.QHBoxLayout()
        tool_excl_lay.addWidget(tool_grp_excl_true)
        tool_excl_lay.addStretch()

        tool_grp_excl_false = MToolButtonGroup(
            orientation=QtCore.Qt.Orientation.Horizontal, exclusive=False
        )
        tool_grp_excl_false.set_button_list(
            [
                MButtonGroupData(tooltip="bold", svg="bold.svg", checkable=True),
                MButtonGroupData(tooltip="italic", svg="italic.svg", checkable=True),
                MButtonGroupData(
                    tooltip="underline", svg="underline.svg", checkable=True
                ),
            ]
        )
        tool_excl_2_lay = QtWidgets.QHBoxLayout()
        tool_excl_2_lay.addWidget(tool_grp_excl_false)
        tool_excl_2_lay.addStretch()

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("orientation=Qt.Horizontal "))
        main_lay.addLayout(tool_1_lay)
        main_lay.addWidget(MDivider("orientation=Qt.Vertical"))
        main_lay.addWidget(tool_group_v)
        main_lay.addWidget(MDivider("orientation=Qt.Horizontal"))
        main_lay.addLayout(tool_2_lay)
        main_lay.addWidget(MDivider("checkable=True; exclusive=True"))
        main_lay.addLayout(tool_excl_lay)
        main_lay.addWidget(MDivider("checkable=True; exclusive=False"))
        main_lay.addLayout(tool_excl_2_lay)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = ToolButtonGroupExample()
        MTheme().apply(test)
        test.show()
