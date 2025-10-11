"""
MSwitch
"""

from __future__ import annotations

from qtpy import QtCore, QtWidgets

from .mixin import cursor_mixin
from .theme import MTheme


@cursor_mixin
class MSwitch(QtWidgets.QRadioButton):
    """
    Switching Selector.

    Property:
        dayu_size: the size of switch widget. int
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._dayu_size: int = MTheme().default_size
        self.setAutoExclusive(False)

    def minimumSizeHint(self) -> QtCore.QSize:  # noqa: N802
        """
        Override the QRadioButton minimum size hint. We don't need the text space.
        :return:
        """
        height = self._dayu_size * 1.2
        return QtCore.QSize(int(height), int(height / 2))

    def get_dayu_size(self) -> int:
        """
        Get the switch size.
        :return: int
        """
        return self._dayu_size

    def set_dayu_size(self, value: int) -> None:
        """
        Set the switch size.
        :param value: int
        :return: None
        """
        self._dayu_size = value
        self.style().polish(self)

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def huge(self) -> MSwitch:
        """Set MSwitch to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MSwitch to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MSwitch to medium size"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MSwitch to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MSwitch to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self
