"""MFlowLayout"""

from qtpy import QtCore, QtWidgets


class MFlowLayout(QtWidgets.QLayout):
    """
    FlowLayout, the code is come from PySide/examples/layouts/flowlayout.py
    I change the code style and add insertWidget method.
    """

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        margin: int = 0,
        spacing: int = -1,
    ):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self.item_list: list[QtWidgets.QLayoutItem] = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def insertWidget(self, index: int, widget: QtWidgets.QWidget):  # noqa: N802
        self.addChildWidget(widget)
        if index < 0:
            index = self.count()
        item = QtWidgets.QWidgetItem(widget)
        self.item_list.insert(index, item)
        self.update()

    def addItem(self, item: QtWidgets.QLayoutItem):  # noqa: N802
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index: int):  # noqa: N802
        if 0 <= index < len(self.item_list):
            return self.item_list[index]

        return None

    def takeAt(self, index: int):  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index).widget()

        return None

    def clear(self):
        while self.item_list:
            widget = self.takeAt(0)
            if widget:
                widget.deleteLater()

    def expandingDirections(self) -> QtCore.Qt.Orientation:  # noqa: N802
        return QtCore.Qt.Orientation.Horizontal

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        height = self.do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect: QtCore.QRect):  # noqa: N802
        super().setGeometry(rect)
        self.do_layout(rect, False)

    def sizeHint(self) -> QtCore.QSize:  # noqa: N802
        return self.minimumSize()

    def minimumSize(self) -> QtCore.QSize:  # noqa: N802
        size = QtCore.QSize()

        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(
            2 * self.contentsMargins().top(), 2 * self.contentsMargins().top()
        )
        return size

    def do_layout(self, rect: QtCore.QRect, test_only: bool) -> int:
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self.item_list:
            if not (wid := item.widget()):
                continue

            space_x = self.spacing() + wid.style().layoutSpacing(
                QtWidgets.QSizePolicy.ControlType.PushButton,
                QtWidgets.QSizePolicy.ControlType.PushButton,
                QtCore.Qt.Orientation.Horizontal,
            )
            space_y = self.spacing() + wid.style().layoutSpacing(
                QtWidgets.QSizePolicy.ControlType.PushButton,
                QtWidgets.QSizePolicy.ControlType.PushButton,
                QtCore.Qt.Orientation.Vertical,
            )
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()
