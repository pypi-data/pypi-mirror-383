from typing import TYPE_CHECKING, cast

from qtpy import QtCore, QtWidgets

from .theme import MTheme


class MWidget(QtWidgets.QWidget if TYPE_CHECKING else object):
    """
    Base class for all widgets.

    Properties:
        dayu_type: str (default: "")
        dayu_size: int (default: MTheme().default_size)
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__()
        self._dayu_type: str = ""
        self._dayu_size: int = MTheme().default_size

    def get_dayu_type(self) -> str:
        return self._dayu_type

    def set_dayu_type(self, value: str):
        if value != self._dayu_type:
            self._dayu_type = value
            self.on_style_changed()

    def get_dayu_size(self) -> int:
        return self._dayu_size

    def set_dayu_size(self, value: int):
        if value != self._dayu_size:
            self._dayu_size = value
            self.on_style_changed()

    def style(self) -> QtWidgets.QStyle: ...

    def on_style_changed(self):
        self.style().polish(cast(QtWidgets.QWidget, self))

    dayu_type = QtCore.Property(str, get_dayu_type, set_dayu_type)
    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)
