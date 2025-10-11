from qtpy import QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel


class DividerExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MDivider")
        self._init_ui()

    def _init_ui(self):
        div1 = MDivider()
        div2 = MDivider("With Text")
        div3 = MDivider.left("Left Text")
        div4 = MDivider.center("Center Text")
        div5 = MDivider.right("Right Text")
        div6 = MDivider.vertical()
        div7 = MDivider.vertical()
        div8 = MDivider.left("orientation=Qt.Vertical")
        label1 = MLabel("Maya").strong()
        label2 = MLabel("Nuke").underline()
        label3 = MLabel("Houdini").mark()
        sub_lay = QtWidgets.QHBoxLayout()
        sub_lay.addWidget(label1)
        sub_lay.addWidget(div6)
        sub_lay.addWidget(label2)
        sub_lay.addWidget(div7)
        sub_lay.addWidget(label3)
        sub_lay.addStretch()

        some_text = (
            "Steven Paul Jobs was an American entrepreneur and business magnate."
        )
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MLabel(some_text))
        main_lay.addWidget(div1)
        main_lay.addWidget(MLabel(some_text))
        main_lay.addWidget(div2)
        main_lay.addWidget(MLabel(some_text))
        main_lay.addWidget(div3)
        main_lay.addWidget(MLabel(some_text))
        main_lay.addWidget(div4)
        main_lay.addWidget(MLabel(some_text))
        main_lay.addWidget(div5)
        main_lay.addLayout(sub_lay)
        main_lay.addWidget(div8)
        main_lay.addStretch()
        self.setLayout(main_lay)

    def computed_text(self):
        return "Clicked: " + str(self.field("count"))

    def slot_change_divider_text(self):
        self.set_field("count", self.field("count") + 1)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = DividerExample()
        MTheme().apply(test)
        test.show()
