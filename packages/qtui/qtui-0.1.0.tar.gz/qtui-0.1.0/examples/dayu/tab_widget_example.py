from qtpy import QtCore, QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.label import MLabel
from qtui.dayu.message import MMessage
from qtui.dayu.tab_widget import MTabWidget


class TabWidgetExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()
        self.resize(500, 500)

    def _init_ui(self):
        main_lay = QtWidgets.QVBoxLayout()

        tab_card = MTabWidget()
        tab_card.addTab(MLabel("test 1"), "Current Element")
        tab_card.addTab(MLabel("test 2"), "Linked Assets")
        tab_card.addTab(MLabel("test 2"), "Hero Shots")
        tab_card.addTab(MLabel("test 3"), "Linked Metadata")

        self.tab_closable = MTabWidget()
        self.tab_closable.setTabsClosable(True)
        self.tab_closable.addTab(MLabel("test 1"), "Label One")
        self.tab_closable.addTab(MLabel("test 2"), "Label Two")
        self.tab_closable.addTab(MLabel("test 3"), "Label Three")
        self.tab_closable.tabCloseRequested.connect(self.slot_close_tab)
        main_lay.addWidget(MDivider("Normal"))
        main_lay.addWidget(tab_card)
        main_lay.addWidget(MDivider("Closable"))
        main_lay.addWidget(self.tab_closable)
        self.setLayout(main_lay)

    @QtCore.Slot(int)
    def slot_close_tab(self, index: int):
        if index > 0:
            text = self.tab_closable.tabText(index)
            self.tab_closable.removeTab(index)
            MMessage.info(
                f"Successfully closed a label: {text}", closable=True, parent=self
            )
        else:
            MMessage.warning(
                "Please do not close the first label", closable=True, parent=self
            )


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = TabWidgetExample()
        MTheme().apply(test)
        test.show()
