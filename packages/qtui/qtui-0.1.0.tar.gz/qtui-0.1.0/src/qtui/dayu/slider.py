"""MSlider"""

# Import third-party modules
from qtpy import QtCore, QtGui, QtWidgets


class MSlider(QtWidgets.QSlider):
    """
    A Slider component for displaying current value and intervals in range.

    MSlider just apply qss for QSlider.
    """

    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(orientation, parent=parent)
        self._show_text_when_move = True

    def disable_show_text(self):
        self._show_text_when_move = False

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):  # noqa: N802
        """Override the mouseMoveEvent to show current value as a tooltip."""
        if self._show_text_when_move:
            QtWidgets.QToolTip.showText(event.globalPos(), str(self.value()), self)
        return super().mouseMoveEvent(event)
