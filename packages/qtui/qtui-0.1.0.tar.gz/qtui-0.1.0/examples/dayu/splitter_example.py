"""
Example code for MSplitter
"""

from qtpy import QtCore, QtWidgets

from qtui.dayu.splitter import MSplitter
from qtui.dayu.text_edit import MTextEdit
from qtui.dayu.theme import MTheme


class SplitterExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        main_splitter = MSplitter(QtCore.Qt.Orientation.Vertical)
        main_splitter.setHandleWidth(20)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        container.setLayout(layout)
        splitter = MSplitter(QtCore.Qt.Orientation.Vertical)
        splitter.addWidget(MTextEdit())
        splitter.addWidget(MTextEdit())
        splitter.addWidget(MTextEdit())
        layout.addWidget(splitter)
        main_splitter.addWidget(container)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        container.setLayout(layout)
        splitter = MSplitter()
        splitter.addWidget(MTextEdit())
        splitter.addWidget(MTextEdit())
        splitter.addWidget(MTextEdit())
        layout.addWidget(splitter)
        main_splitter.addWidget(container)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(main_splitter)
        self.setLayout(layout)

        self.resize(800, 800)


if __name__ == "__main__":
    from qtui.dayu.qt import application

    with application() as app:
        test = SplitterExample()
        MTheme().apply(test)
        test.show()
