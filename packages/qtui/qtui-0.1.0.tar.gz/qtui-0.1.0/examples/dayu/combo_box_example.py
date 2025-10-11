import random

from qtpy import QtWidgets

from qtui.dayu.combo_box import MComboBox
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.menu import MMenu
from qtui.dayu.theme import MTheme
from qtui.dayu.types import MenuItemData


class ComboBoxExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        cities = ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"]
        self.register_field("button1_selected", "Beijing")
        menu1 = MMenu(parent=self)
        menu1.set_data(cities)
        size_list = [
            ("Large", MTheme().large),
            ("Medium", MTheme().medium),
            ("Small", MTheme().small),
        ]
        size_lay = QtWidgets.QHBoxLayout()
        for _label, size in size_list:
            combo_box = MComboBox()
            combo_box.set_dayu_size(size)
            combo_box.set_menu(menu1)
            size_lay.addWidget(combo_box)
            self.bind("button1_selected", combo_box, "value", signal="value_changed")

        self.register_field("button2_selected", ["Beijing"])
        menu2 = MMenu(exclusive=False, parent=self)
        menu2.set_data(cities)
        select2 = MComboBox()
        select2.set_menu(menu2)
        self.bind("button2_selected", select2, "value", signal="value_changed")

        def dynamic_get_city() -> list[str]:
            data = [*cities, "Zhengzhou", "Shijiazhuang"]
            start = random.randint(0, len(data))
            end = random.randint(start, len(data))
            return data[start:end]

        self.register_field("button3_selected", "")
        menu3 = MMenu(parent=self)
        menu3.set_load_callback(dynamic_get_city)
        select3 = MComboBox()
        select3.set_menu(menu3)
        self.bind("button3_selected", select3, "value", signal="value_changed")

        menu4_items = [
            MenuItemData(
                children=[
                    MenuItemData(value="Forbidden City", label="Forbidden City"),
                    MenuItemData(value="Temple of Heaven", label="Temple of Heaven"),
                    MenuItemData(value="Wangfujing", label="Wangfujing"),
                ],
                value="Beijing",
                label="Beijing",
            ),
            MenuItemData(
                children=[
                    MenuItemData(
                        children=[
                            MenuItemData(
                                value="Confucius Temple",
                                label="Confucius Temple",
                            ),
                        ],
                        value="Nanjing",
                        label="Nanjing",
                    ),
                    MenuItemData(
                        children=[
                            MenuItemData(
                                value="Humble Garden",
                                label="Humble Garden",
                            ),
                            MenuItemData(
                                value="Lion Grove",
                                label="Lion Grove",
                            ),
                        ],
                        value="Suzhou",
                        label="Suzhou",
                    ),
                ],
                value="Jiangsu",
                label="Jiangsu",
            ),
        ]

        self.register_field("button4_selected", "")
        menu4 = MMenu(cascader=True, parent=self)
        menu4.set_data(menu4_items)
        select4 = MComboBox()
        select4.set_menu(menu4)
        select4.set_formatter(lambda x: " / ".join(x))
        self.bind("button4_selected", select4, "value", signal="value_changed")

        self.register_field("button5_selected", "")
        menu5 = MMenu(exclusive=False, parent=self)
        menu5.set_data(cities)
        select5 = MComboBox()
        select5.set_menu(menu5)
        select5.set_formatter(lambda x: " & ".join(x))
        self.bind("button5_selected", select5, "value", signal="value_changed")

        sub_lay1 = QtWidgets.QHBoxLayout()
        sub_lay1.addWidget(MLabel("Single Selection - Various Sizes"))
        sub_lay1.addLayout(size_lay)
        sub_lay1.addStretch()
        sub_lay2 = QtWidgets.QHBoxLayout()
        sub_lay2.addWidget(MLabel("Multiple Selection"))
        sub_lay2.addWidget(select2)
        sub_lay2.addStretch()
        sub_lay3 = QtWidgets.QHBoxLayout()
        sub_lay3.addWidget(MLabel("Dynamic Options"))
        sub_lay3.addWidget(select3)
        sub_lay3.addStretch()
        sub_lay4 = QtWidgets.QHBoxLayout()
        sub_lay4.addWidget(MLabel("Cascading Selection"))
        sub_lay4.addWidget(select4)
        sub_lay4.addStretch()
        sub_lay5 = QtWidgets.QHBoxLayout()
        sub_lay5.addWidget(MLabel("Custom Display"))
        sub_lay5.addWidget(select5)
        sub_lay5.addStretch()

        sub_lay6 = QtWidgets.QHBoxLayout()
        combo = MComboBox()
        items = [*cities, "Beidaihe"]

        items += ["a" * i for i in range(20)]
        combo.addItems(items)
        combo.setProperty("searchable", True)
        sub_lay6.addWidget(MLabel("Search Autocomplete"))
        sub_lay6.addWidget(combo)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Select"))
        main_lay.addLayout(sub_lay1)
        main_lay.addLayout(sub_lay2)
        main_lay.addLayout(sub_lay3)
        main_lay.addWidget(MDivider("Custom Format"))
        main_lay.addLayout(sub_lay4)
        main_lay.addLayout(sub_lay5)
        main_lay.addLayout(sub_lay6)
        main_lay.addStretch()

        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application

    with application() as app:
        test = ComboBoxExample()
        MTheme().apply(test)
        test.show()
