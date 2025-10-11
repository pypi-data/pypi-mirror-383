"""MToolButton"""

from qtpy import QtCore, QtGui, QtWidgets

from .mixin import cursor_mixin
from .qt import MIcon
from .theme import MTheme
from .widget import MWidget


@cursor_mixin
class MToolButton(QtWidgets.QToolButton, MWidget):
    """MToolButton"""

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self._svg: str = ""
        self.setAutoExclusive(False)
        self.setAutoRaise(True)

        self._polish_icon()
        self.toggled.connect(self._polish_icon)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

    @QtCore.Slot()
    def _polish_icon(self):
        if self._svg:
            if self.isCheckable() and self.isChecked():
                self.setIcon(MIcon(self._svg, MTheme().primary_color))
            else:
                self.setIcon(MIcon(self._svg))

    def enterEvent(self, event: QtGui.QEnterEvent):  # noqa: N802
        """Override enter event to highlight the icon"""
        if self._svg:
            self.setIcon(MIcon(self._svg, MTheme().primary_color))
        return super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent):  # noqa: N802
        """Override leave event to recover the icon"""
        self._polish_icon()
        return super().leaveEvent(event)

    def get_dayu_size(self) -> int:
        """
        Get the push button height
        :return: integer
        """
        return self._dayu_size

    def set_dayu_size(self, value: int):
        """
        Set the avatar size.
        :param value: integer
        :return: None
        """
        if value != self._dayu_size:
            super().set_dayu_size(value)
            if self.toolButtonStyle() == QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly:
                self.setFixedSize(QtCore.QSize(self._dayu_size, self._dayu_size))

    def get_svg(self):
        """Get current svg path"""
        return self._svg

    def set_svg(self, name: str):
        """Set current svg path"""
        self._svg = name
        self._polish_icon()

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def huge(self):
        """Set MPushButton to PrimaryType"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MPushButton to SuccessType"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MPushButton to  WarningType"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MPushButton to DangerType"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MPushButton to DangerType"""
        self.set_dayu_size(MTheme().tiny)
        return self

    def svg(self, name: str):
        """Set current svg path"""
        self.set_svg(name)
        return self

    def icon_only(self):
        """Set tool button style to icon only"""
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setFixedSize(QtCore.QSize(self._dayu_size, self._dayu_size))
        return self

    def text_only(self):
        """Set tool button style to text only"""
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
        return self

    def text_beside_icon(self):
        """Set tool button style to text beside icon"""
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        return self

    def text_under_icon(self):
        """Set tool button style to text under icon"""
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        return self
