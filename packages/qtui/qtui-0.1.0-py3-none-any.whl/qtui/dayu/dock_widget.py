"""MDockWidget"""

from qtpy import QtCore, QtWidgets


class MDockWidget(QtWidgets.QDockWidget):
    """
    Just apply the qss. No more extend.
    """

    def __init__(
        self,
        title: str = "",
        parent: QtWidgets.QWidget | None = None,
        flags: QtCore.Qt.WindowType = QtCore.Qt.WindowType.Widget,
    ):
        super().__init__(title, parent=parent, flags=flags)
