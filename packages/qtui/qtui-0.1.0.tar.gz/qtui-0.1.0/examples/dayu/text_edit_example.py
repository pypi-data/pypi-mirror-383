from qtpy import QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.push_button import MPushButton
from qtui.dayu.text_edit import MTextEdit


class TextEditExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_lay = QtWidgets.QVBoxLayout()

        main_lay.addWidget(MDivider("no size grip"))
        main_lay.addWidget(MTextEdit(self))
        main_lay.addWidget(MDivider("size grip"))
        main_lay.addWidget(MTextEdit(self).resizeable())
        main_lay.addWidget(MPushButton("text").primary())

        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = TextEditExample()
        MTheme().apply(test)
        test.show()
