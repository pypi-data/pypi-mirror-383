"""
MCollapse
"""

from __future__ import annotations

from qtpy import QtCore, QtWidgets

from .label import MLabel
from .mixin import property_mixin
from .qt import MPixmap
from .tool_button import MToolButton


@property_mixin
class MCollapse(QtWidgets.QWidget):
    sig_context_menu = QtCore.Signal(object)

    def __init__(
        self,
        title: str = "",
        content: QtWidgets.QWidget | None = None,
        expand: bool = False,
        closable: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)

        self.title_label = MLabel(parent=self)
        self.expand_icon = MLabel(parent=self)
        self.expand_icon.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self._close_button = MToolButton().icon_only().tiny().svg("close_line.svg")
        self._close_button.clicked.connect(self.close)
        self._closable = closable
        self._expand = expand
        self._content = content

        self._central_widget = None

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.expand_icon)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self._close_button)

        self.header_widget = QtWidgets.QWidget(parent=self)
        self.header_widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        self.header_widget.setObjectName("title")
        self.header_widget.setLayout(header_layout)
        self.header_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.header_widget.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.title_label.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.header_widget.installEventFilter(self)
        self.title_label.installEventFilter(self)

        self.content_widget = QtWidgets.QWidget(parent=self)
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_widget.setLayout(self.content_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.header_widget)
        self.main_layout.addWidget(self.content_widget)
        self.setLayout(self.main_layout)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.setMouseTracking(True)

        self.set_title(title)
        self.set_content(content)
        self.closable(closable)
        self.expand(expand)

    def set_title(self, value: str) -> None:
        self.title_label.setText(value)

    def set_content(self, widget: QtWidgets.QWidget | None) -> None:
        if widget is not None:
            if self._content:
                self.content_layout.removeWidget(self._content)
                self._content.close()
            self.content_layout.addWidget(widget)
            self._content = widget

    def content(self) -> QtWidgets.QWidget | None:
        return self._content

    def closable(self, value: bool = True) -> MCollapse:
        self._closable = value
        self.content_widget.setVisible(value)
        self._close_button.setVisible(value)
        return self

    def expand(self, value: bool = True) -> MCollapse:
        self._expand = value
        self.content_widget.setVisible(value)
        self.expand_icon.setPixmap(
            MPixmap("down_line.svg" if value else "right_line.svg").scaledToHeight(12)
        )
        return self

    def eventFilter(self, widget: QtWidgets.QWidget, event: QtCore.QEvent) -> bool:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        if (
            widget in [self.header_widget, self.title_label]
            and event.type() == QtCore.QEvent.Type.MouseButtonRelease
        ):
            self.expand(not self._expand)
        return super().eventFilter(widget, event)
