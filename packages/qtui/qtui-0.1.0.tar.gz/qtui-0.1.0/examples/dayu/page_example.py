from qtpy import QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.page import MPage


class PageExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MPage")
        self._init_ui()

    def _init_ui(self):
        page_1 = MPage()
        page_1.set_total(255)
        page_1.sig_page_changed.connect(print)

        page_2 = MPage()
        page_2.set_total(100)

        main_lay = QtWidgets.QVBoxLayout()
        self.setLayout(main_lay)
        main_lay.addWidget(MDivider())
        main_lay.addWidget(page_1)
        main_lay.addWidget(MDivider())
        main_lay.addWidget(page_2)
        main_lay.addStretch()


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = PageExample()
        MTheme().apply(test)
        test.show()
