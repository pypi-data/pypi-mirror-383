from qtpy import QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.menu import MMenu
from qtui.dayu.push_button import MPushButton


class MenuExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.register_field("button1_selected", "Beijing")
        self.register_field(
            "button1_selected_text", lambda: self.field("button1_selected")
        )
        button1 = MPushButton(text="Normal Menu")
        menu1 = MMenu(parent=self)
        menu1.set_data(["Beijing", "Shanghai", "Guangzhou", "Shenzhen"])
        button1.setMenu(menu1)
        button1.clicked.connect(button1.showMenu)
        label1 = MLabel()

        self.bind("button1_selected", menu1, "value", signal="value_changed")
        self.bind("button1_selected_text", label1, "text")

        self.register_field("button2_selected", ["Beijing"])
        self.register_field(
            "button2_selected_text", lambda: ", ".join(self.field("button2_selected"))
        )
        button2 = MPushButton(text="Multi Select Menu")
        menu2 = MMenu(exclusive=False, parent=self)
        menu2.set_data(["Beijing", "Shanghai", "Guangzhou", "Shenzhen"])
        button2.setMenu(menu2)
        button2.clicked.connect(button2.showMenu)
        label2 = MLabel()
        self.bind("button2_selected", menu2, "value", signal="value_changed")
        self.bind("button2_selected_text", label2, "text")

        self.register_field("button3_selected", "")
        self.register_field(
            "button3_selected_text", lambda: self.field("button3_selected")
        )
        button3 = MPushButton(text="Callback Function Get Options")
        menu3 = MMenu(parent=self)
        menu3.set_load_callback(
            lambda: ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Seoul"]
        )
        button3.setMenu(menu3)
        button3.clicked.connect(button2.showMenu)
        label3 = MLabel()
        self.bind("button3_selected", menu3, "value", signal="value_changed")
        self.bind("button3_selected_text", label3, "text")

        self.register_field("button4_selected", "")
        self.register_field(
            "button4_selected_text", lambda: " / ".join(self.field("button4_selected"))
        )
        button4 = MPushButton(text="Cascader Select")
        menu4 = MMenu(cascader=True, parent=self)
        menu4.set_data(
            [
                "Beijing/Forbidden City",
                "Beijing/Tiananmen",
                "Beijing/Wangfujing",
                "Jiangsu/Nanjing/Confucius Temple",
                "Jiangsu/Suzhou/Zhuozhengyuan",
                "Jiangsu/Suzhou/Lion Grove",
            ]
        )
        button4.setMenu(menu4)
        button4.clicked.connect(button4.showMenu)
        label4 = MLabel()
        self.bind("button4_selected", menu4, "value", signal="value_changed")
        self.bind("button4_selected_text", label4, "text")

        sub_lay1 = QtWidgets.QHBoxLayout()
        sub_lay1.addWidget(button1)
        sub_lay1.addWidget(label1)
        sub_lay2 = QtWidgets.QHBoxLayout()
        sub_lay2.addWidget(button2)
        sub_lay2.addWidget(label2)
        sub_lay3 = QtWidgets.QHBoxLayout()
        sub_lay3.addWidget(button3)
        sub_lay3.addWidget(label3)
        sub_lay4 = QtWidgets.QHBoxLayout()
        sub_lay4.addWidget(button4)
        sub_lay4.addWidget(label4)

        sub_lay5 = QtWidgets.QHBoxLayout()
        button = MPushButton(text="Scroll Menu")
        menu = MMenu(parent=self)
        items = [
            "Beijing",
            "Shanghai",
            "Guangzhou",
            "Shenzhen",
            "Beidaihe",
            "BBC/data",
            "BBC/hello",
            "American",
        ]
        menu.set_data(items)
        menu.setProperty("max_scroll_count", 3)
        menu.setProperty("scrollable", True)
        menu.setProperty("searchable", True)
        button.setMenu(menu)
        sub_lay5.addWidget(button)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Select"))
        main_lay.addLayout(sub_lay1)
        main_lay.addLayout(sub_lay2)
        main_lay.addLayout(sub_lay3)
        main_lay.addWidget(MDivider("Cascader Select"))
        main_lay.addLayout(sub_lay4)
        main_lay.addLayout(sub_lay5)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = MenuExample()
        MTheme().apply(test)
        test.show()
