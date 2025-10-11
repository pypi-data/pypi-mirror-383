from qtpy import QtWidgets

from qtui.dayu.avatar import MAvatar
from qtui.dayu.badge import MBadge
from qtui.dayu.combo_box import MComboBox
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.menu import MMenu
from qtui.dayu.qt import MPixmap
from qtui.dayu.spin_box import MSpinBox
from qtui.dayu.theme import MTheme
from qtui.dayu.tool_button import MToolButton


class BadgeExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MBadge")
        self._init_ui()

    def _init_ui(self):
        standalone_lay = QtWidgets.QHBoxLayout()
        standalone_lay.addWidget(MBadge.count(0))
        standalone_lay.addWidget(MBadge.count(20))
        standalone_lay.addWidget(MBadge.count(100))
        standalone_lay.addWidget(MBadge.dot(True))
        standalone_lay.addWidget(MBadge.text("new"))
        standalone_lay.addStretch()

        button = MToolButton().svg("trash_line.svg")
        avatar = MAvatar.large(MPixmap("avatar.png"))
        button_alert = MToolButton().svg("alert_fill.svg").large()
        badge_1 = MBadge.dot(True, widget=button)
        badge_2 = MBadge.dot(True, widget=avatar)
        badge_3 = MBadge.dot(True, widget=button_alert)
        button.clicked.connect(lambda: badge_1.set_dayu_dot(not badge_1.get_dayu_dot()))

        spin_box = MSpinBox()
        spin_box.setRange(0, 9999)
        spin_box.valueChanged.connect(badge_3.set_dayu_count)
        spin_box.setValue(1)

        self.register_field("button1_selected", "Beijing")
        menu1 = MMenu(parent=self)
        menu1.set_data(["Beijing", "Shanghai", "Guangzhou", "Shenzhen"])
        select1 = MComboBox()
        select1.set_menu(menu1)
        self.bind("button1_selected", select1, "value", signal="value_changed")

        badge_hot = MBadge.text("hot", widget=MLabel("Your ideal city  "))

        sub_lay1 = QtWidgets.QHBoxLayout()
        sub_lay1.addWidget(badge_1)
        sub_lay1.addWidget(badge_2)
        sub_lay1.addWidget(badge_3)
        sub_lay1.addStretch()

        sub_lay2 = QtWidgets.QHBoxLayout()
        sub_lay2.addWidget(badge_hot)
        sub_lay2.addWidget(select1)
        sub_lay2.addStretch()

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("use standalone"))
        main_lay.addLayout(standalone_lay)
        main_lay.addWidget(MDivider("different type"))
        main_lay.addLayout(sub_lay1)
        main_lay.addWidget(spin_box)
        main_lay.addWidget(MDivider("different type"))
        main_lay.addLayout(sub_lay2)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = BadgeExample()
        MTheme().apply(test)
        test.show()
